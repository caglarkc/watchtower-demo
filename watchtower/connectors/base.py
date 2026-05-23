"""Connector protocol base class."""

from __future__ import annotations

from abc import ABC, abstractmethod

from watchtower.domain.events import (
    ConnectorCursor,
    EventBatch,
    SourceHealth,
    SourceSchemaHint,
)


class ConnectorError(Exception):
    """Raised when a connector operation fails."""


class BaseConnector(ABC):
    """Read-only connector contract: health, poll, ack, schema_hint."""

    connector_type: str

    def __init__(self, source_id: str, *, read_only: bool = True) -> None:
        self.source_id = source_id
        if not read_only:
            msg = "Watchtower connectors must be read-only"
            raise ValueError(msg)

    @abstractmethod
    def health(self) -> SourceHealth:
        """Return source reachability and readiness."""

    @abstractmethod
    def poll(self, cursor: ConnectorCursor, limit: int) -> EventBatch:
        """Fetch up to ``limit`` raw events after ``cursor``."""

    @abstractmethod
    def ack(self, cursor: ConnectorCursor) -> None:
        """Acknowledge successful processing of events up to ``cursor``."""

    @abstractmethod
    def schema_hint(self) -> SourceSchemaHint:
        """Describe expected payload shape for normalization."""
