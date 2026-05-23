"""Wazuh-compatible REST adapter skeleton (read-only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any, Callable

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.domain.events import (
    ConnectorCursor,
    EventBatch,
    RawEventRecord,
    SourceHealth,
    SourceSchemaHint,
)
from watchtower.ingest.dedupe import dedupe_key_from_parts


class WazuhConnector(BaseConnector):
    """Skeleton adapter for Wazuh API v4 style endpoints."""

    connector_type = "wazuh"

    def __init__(
        self,
        source_id: str,
        *,
        api_url: str,
        username: str | None = None,
        password: str | None = None,
        token: str | None = None,
        http_get: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(source_id)
        self.api_url = api_url.rstrip("/")
        self.username = username
        self.password = password
        self._token = token
        self._http_get = http_get or self._default_get

    def _default_get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        request = urllib.request.Request(url, method="GET", headers=headers or {})
        try:
            with urllib.request.urlopen(request, timeout=10.0) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectorError(str(exc)) from exc

    def _auth_headers(self) -> dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return {}

    def health(self) -> SourceHealth:
        try:
            payload = self._http_get(f"{self.api_url}/", self._auth_headers())
        except ConnectorError as exc:
            return SourceHealth(status="unhealthy", message=str(exc))
        return SourceHealth(
            status="healthy",
            message="wazuh api reachable",
            details={"title": payload.get("title", "wazuh")},
        )

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        offset = int(cursor.data.get("offset", 0))
        url = f"{self.api_url}/events?q=offset={offset};limit={limit}"
        try:
            payload = self._http_get(url, self._auth_headers())
        except ConnectorError:
            raise

        items = payload.get("data", {}).get("affected_items", [])
        if items is None:
            items = payload.get("data", [])
        if not isinstance(items, list):
            items = []

        events: list[RawEventRecord] = []
        for item in items[:limit]:
            if not isinstance(item, dict):
                item = {"_value": item}
            alert_id = str(item.get("id", item.get("_id", offset + len(events))))
            ts_raw = item.get("timestamp") or item.get("@timestamp")
            ts = None
            if ts_raw:
                try:
                    ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
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
        next_cursor = ConnectorCursor(data={**cursor.data, "offset": next_offset})
        has_more = len(items) >= limit
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="wazuh_alert",
            fields=["id", "timestamp", "rule", "agent", "data"],
            notes="Skeleton — map to unified schema in normalization phase",
        )
