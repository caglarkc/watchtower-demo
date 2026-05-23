"""Elasticsearch read-only connector (search_after polling)."""

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
from watchtower.ingest.dedupe import dedupe_key_for_es_doc


class ElasticsearchConnector(BaseConnector):
    connector_type = "elasticsearch"

    def __init__(
        self,
        source_id: str,
        *,
        base_url: str,
        index: str,
        query: dict[str, Any] | None = None,
        http_get: Callable[..., Any] | None = None,
        http_post: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(source_id)
        self.base_url = base_url.rstrip("/")
        self.index = index
        self.query = query or {"match_all": {}}
        self._http_get = http_get or self._default_get
        self._http_post = http_post or self._default_post

    def _default_get(self, url: str, timeout: float = 10.0) -> dict[str, Any]:
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectorError(str(exc)) from exc

    def _default_post(
        self, url: str, body: dict[str, Any], timeout: float = 10.0
    ) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectorError(str(exc)) from exc

    def health(self) -> SourceHealth:
        try:
            payload = self._http_get(f"{self.base_url}/_cluster/health")
        except ConnectorError as exc:
            return SourceHealth(status="unhealthy", message=str(exc))
        status = payload.get("status", "unknown")
        mapped = "healthy" if status in {"green", "yellow"} else "degraded"
        return SourceHealth(
            status=mapped,
            message=f"cluster status: {status}",
            details={"cluster_name": payload.get("cluster_name")},
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
        try:
            result = self._http_post(url, body)
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
        return EventBatch(events=events, next_cursor=next_cursor, has_more=has_more)

    def ack(self, cursor: ConnectorCursor) -> None:
        return None

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(
            format="elasticsearch_hit",
            fields=["@timestamp", "user", "source_ip", "detection_type"],
        )
