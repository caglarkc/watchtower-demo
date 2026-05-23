"""Daemon loop result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourcePollResult:
    source_id: str
    polled: int = 0
    stored: int = 0
    duplicates: int = 0
    skipped_backoff: bool = False
    error: str | None = None
    degraded: bool = False


@dataclass
class DaemonLoopSummary:
    iteration: int = 0
    tenant_id: str = ""
    mode: str = ""
    sources_polled: int = 0
    sources_failed: int = 0
    sources_skipped_backoff: int = 0
    raw_stored: int = 0
    pipeline: dict[str, int] = field(default_factory=dict)
    graph_runs: int = 0
    graph_interrupted: int = 0
    alerts_created: int = 0
    silent_findings: int = 0
    learning_events: int = 0
    source_results: list[SourcePollResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_audit_details(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "mode": self.mode,
            "sources_polled": self.sources_polled,
            "sources_failed": self.sources_failed,
            "raw_stored": self.raw_stored,
            "pipeline": self.pipeline,
            "graph_runs": self.graph_runs,
            "alerts_created": self.alerts_created,
            "silent_findings": self.silent_findings,
            "learning_events": self.learning_events,
            "errors": self.errors,
        }
