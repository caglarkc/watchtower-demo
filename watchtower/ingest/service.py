"""Ingest orchestration with graceful connector failure handling."""

from __future__ import annotations

import logging

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.connectors.factory import build_connector
from watchtower.domain.events import ConnectorCursor, IngestResult, SourceHealth
from watchtower.domain.source import SourceRecord
from watchtower.storage.repositories.raw_event import RawEventRepository
from watchtower.storage.repositories.source import SourceRepository
from watchtower.storage.repositories.source_cursor import SourceCursorRepository

logger = logging.getLogger(__name__)


class IngestService:
    def __init__(
        self,
        sources: SourceRepository,
        cursors: SourceCursorRepository,
        raw_events: RawEventRepository,
    ) -> None:
        self._sources = sources
        self._cursors = cursors
        self._raw_events = raw_events

    def ingest_once(
        self,
        tenant_id: str,
        source_id: str,
        *,
        limit: int = 500,
    ) -> IngestResult:
        source = self._sources.get(source_id, tenant_id=tenant_id)
        if source is None:
            return IngestResult(
                source_id=source_id,
                error=f"source not found: {source_id}",
                health_status="unhealthy",
                degraded=True,
            )
        if not source.enabled:
            return IngestResult(
                source_id=source_id,
                error="source is disabled",
                health_status="unhealthy",
                degraded=True,
            )

        connector = build_connector(source)
        health = self._safe_health(connector)
        latency_ms = _connector_latency_ms(connector)
        http_retries = _connector_http_retries(connector)
        if health.status == "unhealthy":
            return IngestResult(
                source_id=source_id,
                connector_type=source.connector_type,
                health_status=health.status,
                error=health.message,
                degraded=True,
                latency_ms=latency_ms,
                http_retries=http_retries,
            )

        cursor = self._cursors.get(source_id, tenant_id)
        try:
            batch = connector.poll(cursor, limit)
            latency_ms = _connector_latency_ms(connector) or latency_ms
            http_retries = _connector_http_retries(connector) or http_retries
        except ConnectorError as exc:
            logger.warning("connector poll failed for %s: %s", source_id, exc)
            return IngestResult(
                source_id=source_id,
                connector_type=source.connector_type,
                health_status=health.status,
                error=str(exc),
                degraded=True,
                latency_ms=latency_ms,
                http_retries=http_retries,
            )

        stored = 0
        duplicates = 0
        for event in batch.events:
            if self._raw_events.insert_if_new(tenant_id, source_id, event):
                stored += 1
            else:
                duplicates += 1

        try:
            connector.ack(batch.next_cursor)
            self._cursors.save(source_id, tenant_id, batch.next_cursor, ack=True)
        except ConnectorError as exc:
            logger.warning("connector ack failed for %s: %s", source_id, exc)
            return IngestResult(
                source_id=source_id,
                polled=len(batch.events),
                stored=stored,
                duplicates=duplicates,
                has_more=batch.has_more,
                health_status=health.status,
                error=f"ack failed: {exc}",
                degraded=True,
            )

        return IngestResult(
            source_id=source_id,
            connector_type=source.connector_type,
            polled=len(batch.events),
            stored=stored,
            duplicates=duplicates,
            has_more=batch.has_more,
            health_status=health.status,
            degraded=health.status == "degraded",
            latency_ms=latency_ms,
            http_retries=http_retries,
        )


def _connector_latency_ms(connector: BaseConnector) -> float | None:
    value = getattr(connector, "last_latency_ms", None)
    return float(value) if value is not None else None


def _connector_http_retries(connector: BaseConnector) -> int:
    value = getattr(connector, "http_retries", 0)
    return int(value) if value is not None else 0

    def check_health(self, source: SourceRecord) -> SourceHealth:
        connector = build_connector(source)
        return self._safe_health(connector)

    @staticmethod
    def _safe_health(connector: BaseConnector) -> SourceHealth:
        try:
            return connector.health()
        except ConnectorError as exc:
            return SourceHealth(status="unhealthy", message=str(exc))
        except Exception as exc:  # noqa: BLE001 — graceful degradation
            logger.exception("unexpected connector health error")
            return SourceHealth(status="unhealthy", message=str(exc))
