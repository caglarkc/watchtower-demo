"""Record and read runtime metrics from the product database."""

from __future__ import annotations

from watchtower.daemon.models import DaemonLoopSummary
from watchtower.domain.events import IngestResult
from watchtower.observability.metrics import (
    METRIC_ALERTS,
    METRIC_CANDIDATES,
    METRIC_EVENTS_POLLED,
    METRIC_GRAPH_RUNS,
    METRIC_LLM_CALLS,
    METRIC_NORMALIZED,
    METRIC_RAW_STORED,
    METRIC_SOURCE_ERRORS,
    MetricsSnapshot,
)
from watchtower.storage.repositories.metrics import MetricsRepository


class MetricsService:
    def __init__(self, repo: MetricsRepository) -> None:
        self._repo = repo

    def increment(
        self,
        tenant_id: str,
        metric_name: str,
        delta: float = 1.0,
    ) -> float:
        return self._repo.increment(tenant_id, metric_name, delta)

    def record_ingest(self, tenant_id: str, result: IngestResult) -> None:
        if result.polled:
            self.increment(tenant_id, METRIC_EVENTS_POLLED, result.polled)
        if result.stored:
            self.increment(tenant_id, METRIC_RAW_STORED, result.stored)
        if result.error:
            self.increment(tenant_id, METRIC_SOURCE_ERRORS)

    def record_pipeline(
        self,
        tenant_id: str,
        *,
        normalized: int,
        candidates: int,
    ) -> None:
        if normalized:
            self.increment(tenant_id, METRIC_NORMALIZED, normalized)
        if candidates:
            self.increment(tenant_id, METRIC_CANDIDATES, candidates)

    def record_graph_run(self, tenant_id: str, *, alerts: int = 0) -> None:
        self.increment(tenant_id, METRIC_GRAPH_RUNS)
        if alerts:
            self.increment(tenant_id, METRIC_ALERTS, alerts)

    def record_llm_call(self, tenant_id: str | None) -> None:
        tid = tenant_id or "_global"
        self.increment(tid, METRIC_LLM_CALLS)

    def record_daemon_loop(
        self,
        tenant_id: str,
        summary: DaemonLoopSummary,
        *,
        duration_ms: float,
    ) -> None:
        for poll in summary.source_results:
            if poll.skipped_backoff:
                continue
            if poll.polled:
                self.increment(tenant_id, METRIC_EVENTS_POLLED, poll.polled)
            if poll.stored:
                self.increment(tenant_id, METRIC_RAW_STORED, poll.stored)
            if poll.error:
                self.increment(tenant_id, METRIC_SOURCE_ERRORS)
        pl = summary.pipeline
        self.record_pipeline(
            tenant_id,
            normalized=int(pl.get("normalized", 0)),
            candidates=int(pl.get("candidates", 0)),
        )
        if summary.graph_runs:
            self.increment(tenant_id, METRIC_GRAPH_RUNS, summary.graph_runs)
        if summary.alerts_created:
            self.increment(tenant_id, METRIC_ALERTS, summary.alerts_created)
        self._repo.record_loop_duration(tenant_id, duration_ms)

    def snapshot(self, tenant_id: str) -> MetricsSnapshot:
        return MetricsSnapshot(
            tenant_id=tenant_id,
            counters=self._repo.get_snapshot(tenant_id),
        )
