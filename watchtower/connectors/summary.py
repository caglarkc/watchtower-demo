"""Connector operation metrics for audit and daemon summaries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnectorOperationSummary:
    connector_type: str
    source_id: str
    health_status: str = "healthy"
    polled: int = 0
    stored: int = 0
    duplicates: int = 0
    has_more: bool = False
    degraded: bool = False
    error: str | None = None
    latency_ms: float | None = None
    http_retries: int = 0
    cursor_advanced: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def to_audit_details(self) -> dict[str, Any]:
        return {
            "connector_type": self.connector_type,
            "source_id": self.source_id,
            "health_status": self.health_status,
            "polled": self.polled,
            "stored": self.stored,
            "duplicates": self.duplicates,
            "has_more": self.has_more,
            "degraded": self.degraded,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "http_retries": self.http_retries,
            "cursor_advanced": self.cursor_advanced,
            **self.extra,
        }
