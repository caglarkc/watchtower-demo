"""Wazuh REST adapter (read-only, token auth, time-window cursor)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, Callable

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.connectors.http_util import ConnectorHttpClient, HttpClientConfig
from watchtower.domain.events import (
    ConnectorCursor,
    EventBatch,
    RawEventRecord,
    SourceHealth,
    SourceSchemaHint,
)
from watchtower.ingest.dedupe import dedupe_key_from_parts


def _http_config_from_dict(config: dict[str, Any]) -> HttpClientConfig:
    auth_type = config.get("auth_type")
    if auth_type is None and config.get("token"):
        auth_type = "bearer"
    if auth_type is None and config.get("username"):
        auth_type = "basic"
    return HttpClientConfig(
        timeout_seconds=float(config.get("timeout_seconds", 10.0)),
        max_retries=int(config.get("max_retries", 2)),
        backoff_base_seconds=float(config.get("backoff_base_seconds", 0.5)),
        verify_tls=bool(config.get("verify_tls", True)),
        ca_cert_path=config.get("ca_cert_path"),
        auth_type=auth_type,
        username=config.get("username"),
        password=config.get("password"),
        token=config.get("token"),
    )


class WazuhConnector(BaseConnector):
    """Read-only Wazuh API v4 style alerts/events adapter."""

    connector_type = "wazuh"

    def __init__(
        self,
        source_id: str,
        *,
        api_url: str,
        config: dict[str, Any] | None = None,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        time_window_minutes: int = 60,
        http_get: Callable[..., Any] | None = None,
        http_post: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(source_id)
        self.api_url = api_url.rstrip("/")
        merged = dict(config or {})
        if username:
            merged.setdefault("username", username)
        if password:
            merged.setdefault("password", password)
        if token:
            merged.setdefault("token", token)
        self._config = merged
        self._time_window_minutes = int(
            merged.get("time_window_minutes", time_window_minutes)
        )
        self._session_token: str | None = merged.get("token")
        self._http = ConnectorHttpClient(
            _http_config_from_dict(merged),
            http_get=http_get,  # type: ignore[arg-type]
            http_post=http_post,  # type: ignore[arg-type]
        )

    def _auth_headers(self) -> dict[str, str]:
        token = self._ensure_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return self._http.auth_headers()

    def _ensure_token(self) -> str | None:
        if self._session_token:
            return self._session_token
        preset = self._config.get("token")
        if isinstance(preset, str) and preset:
            self._session_token = preset
            return self._session_token
        user = self._config.get("username")
        password = self._config.get("password")
        if not user or not password:
            return None
        import base64

        basic = base64.b64encode(f"{user}:{password}".encode()).decode("ascii")
        url = f"{self.api_url}/security/user/authenticate"
        payload = self._http.post(
            url,
            {},
            headers={"Authorization": f"Basic {basic}"},
        )
        token = payload.get("data", {}).get("token") or payload.get("token")
        if isinstance(token, str) and token:
            self._session_token = token
            self._http._config.token = token
            self._http._config.auth_type = "bearer"
        return self._session_token

    def health(self) -> SourceHealth:
        try:
            payload = self._http.get(f"{self.api_url}/", headers=self._auth_headers())
        except ConnectorError as exc:
            return SourceHealth(
                status="unhealthy",
                message=str(exc),
                details={
                    "retries": self._http.stats.retries,
                    "latency_ms": self._http.stats.last_latency_ms,
                },
            )
        return SourceHealth(
            status="healthy",
            message="wazuh api reachable",
            details={
                "title": payload.get("title", "wazuh"),
                "api_version": payload.get("api_version"),
                "latency_ms": self._http.stats.last_latency_ms,
                "retries": self._http.stats.retries,
                "authenticated": bool(self._ensure_token() or self._config.get("username")),
            },
        )

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        wazuh = cursor.wazuh_state()
        offset = int(wazuh.get("offset", 0))
        time_from = wazuh.get("time_from")
        if not time_from:
            time_from = (
                datetime.now(UTC) - timedelta(minutes=self._time_window_minutes)
            ).isoformat()

        query_parts = [
            f"offset={offset}",
            f"limit={limit}",
            f"timestamp>{time_from}",
        ]
        url = f"{self.api_url}/events?q={';'.join(query_parts)}"
        try:
            payload = self._http.get(url, headers=self._auth_headers())
        except ConnectorError:
            raise

        items = payload.get("data", {}).get("affected_items", [])
        if items is None:
            items = payload.get("data", [])
        if not isinstance(items, list):
            items = []

        events: list[RawEventRecord] = []
        last_ts: str | None = time_from
        for item in items[:limit]:
            if not isinstance(item, dict):
                item = {"_value": item}
            alert_id = str(item.get("id", item.get("_id", offset + len(events))))
            ts_raw = item.get("timestamp") or item.get("@timestamp")
            ts = None
            if ts_raw:
                try:
                    ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                    last_ts = ts.isoformat()
                except ValueError:
                    ts = None
            events.append(
                RawEventRecord(
                    dedupe_key=dedupe_key_from_parts(self.source_id, "wazuh", alert_id),
                    payload=item,
                    source_path=f"wazuh/events/{alert_id}",
                    event_timestamp=ts,
                )
            )

        next_offset = offset + len(events)
        next_cursor = ConnectorCursor(data=dict(cursor.data))
        next_cursor.set_wazuh_state(
            offset=next_offset,
            time_from=time_from,
            last_timestamp=last_ts,
        )
        has_more = len(items) >= limit
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="wazuh_alert",
            fields=["id", "timestamp", "rule", "agent", "data"],
            notes="Time-window + offset pagination; token or basic auth",
        )

    @property
    def http_retries(self) -> int:
        return self._http.stats.retries

    @property
    def last_latency_ms(self) -> float | None:
        return self._http.stats.last_latency_ms
