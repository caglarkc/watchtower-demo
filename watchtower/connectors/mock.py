"""Mock connector for contract tests."""

from __future__ import annotations

from watchtower.connectors.base import BaseConnector, ConnectorError
from watchtower.domain.events import (
    ConnectorCursor,
    EventBatch,
    RawEventRecord,
    SourceHealth,
    SourceSchemaHint,
)


class MockConnector(BaseConnector):
    connector_type = "mock"

    def __init__(
        self,
        source_id: str,
        *,
        events: list[RawEventRecord] | None = None,
        fail_health: bool = False,
        fail_poll: bool = False,
    ) -> None:
        super().__init__(source_id)
        self._events = list(events or [])
        self._fail_health = fail_health
        self._fail_poll = fail_poll
        self._acked: ConnectorCursor | None = None
        self._poll_index = 0

    @property
    def acked_cursor(self) -> ConnectorCursor | None:
        return self._acked

    def health(self) -> SourceHealth:
        if self._fail_health:
            raise ConnectorError("mock health failure")
        return SourceHealth(status="healthy", message="mock connector ok")

    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        if self._fail_poll:
            raise ConnectorError("mock poll failure")
        start = cursor.data.get("index", 0)
        chunk = self._events[start : start + limit]
        next_index = start + len(chunk)
        next_cursor = ConnectorCursor(data={**cursor.data, "index": next_index})
        return EventBatch(
            events=chunk,
            next_cursor=next_cursor,
            has_more=next_index < len(self._events),
        )

    def ack(self, cursor: ConnectorCursor) -> None:
        self._acked = cursor

    def schema_hint(self) -> SourceSchemaHint:
        return SourceSchemaHint(format="mock", fields=["event_type", "timestamp"])
