"""Elasticsearch read-only connector (search_after, auth, TLS, retry)."""

from __future__ import annotations

import time
from datetime import datetime
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
from watchtower.ingest.dedupe import dedupe_key_for_es_doc


def _http_config_from_dict(config: dict[str, Any]) -> HttpClientConfig:
    return HttpClientConfig(
        timeout_seconds=float(config.get("timeout_seconds", 10.0)),
        max_retries=int(config.get("max_retries", 2)),
        backoff_base_seconds=float(config.get("backoff_base_seconds", 0.5)),
        verify_tls=bool(config.get("verify_tls", True)),
        ca_cert_path=config.get("ca_cert_path"),
        auth_type=config.get("auth_type"),
        username=config.get("username"),
        password=config.get("password"),
        token=config.get("token") or config.get("api_key"),
        api_key=config.get("api_key"),
        api_key_header=str(config.get("api_key_header", "Authorization")),
        api_key_prefix=str(config.get("api_key_prefix", "ApiKey")),
    )


class ElasticsearchConnector(BaseConnector):
    connector_type = "elasticsearch"

    def __init__(
        self,
        source_id: str,
        *,
        base_url: str,
        index: str,
        query: dict[str, Any] | None = None,
        http_config: dict[str, Any] | None = None,
        http_get: Callable[..., Any] | None = None,
        http_post: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(source_id)
        self.base_url = base_url.rstrip("/")
        self.index = index
        self.query = query or {"match_all": {}}
        cfg = _http_config_from_dict(http_config or {})
        self._http = ConnectorHttpClient(
            cfg,
            http_get=http_get,  # type: ignore[arg-type]
            http_post=http_post,  # type: ignore[arg-type]
        )

    def health(self) -> SourceHealth:
        try:
            payload = self._http.get(f"{self.base_url}/_cluster/health")
        except ConnectorError as exc:
            return SourceHealth(
                status="unhealthy",
                message=str(exc),
                details={"retries": self._http.stats.retries},
            )
        status = payload.get("status", "unknown")
        mapped = "healthy" if status in {"green", "yellow"} else "degraded"
        return SourceHealth(
            status=mapped,
            message=f"cluster status: {status}",
            details={
                "cluster_name": payload.get("cluster_name"),
                "latency_ms": self._http.stats.last_latency_ms,
                "retries": self._http.stats.retries,
            },
        )

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        search_after = cursor.es_search_after()
        body: dict[str, Any] = {
            "size": limit,
            "sort": [{"@timestamp": "asc"}, {"_id": "asc"}],
            "query": self.query,
        }
        if search_after is not None:
            body["search_after"] = search_after

        url = f"{self.base_url}/{self.index}/_search"
        started = time.monotonic()
        try:
            result = self._http.post(url, body)
        except ConnectorError:
            raise

        hits = result.get("hits", {}).get("hits", [])
        events: list[RawEventRecord] = []
        last_sort: list[Any] | None = None
        for hit in hits:
            doc_id = str(hit.get("_id", ""))
            source = hit.get("_source", {})
            if not isinstance(source, dict):
                source = {"_value": source}
            ts_raw = source.get("@timestamp") or source.get("timestamp")
            ts = None
            if ts_raw:
                try:
                    ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                except ValueError:
                    ts = None
            events.append(
                RawEventRecord(
                    dedupe_key=dedupe_key_for_es_doc(self.source_id, self.index, doc_id),
                    payload=source,
                    source_path=f"{self.index}/{doc_id}",
                    event_timestamp=ts,
                )
            )
            last_sort = hit.get("sort")

        next_cursor = ConnectorCursor(data=dict(cursor.data))
        next_cursor.set_es_search_after(last_sort)
        has_more = len(hits) >= limit
        _ = started  # latency captured in http stats
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="elasticsearch_hit",
            fields=["@timestamp", "user", "source_ip", "detection_type"],
        )

    @property
    def http_retries(self) -> int:
        return self._http.stats.retries

    @property
    def last_latency_ms(self) -> float | None:
        return self._http.stats.last_latency_ms
