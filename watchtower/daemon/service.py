"""Daemon runtime: ingest → normalize → candidate → graph → alert/finding."""

from __future__ import annotations

import logging
import time
from typing import Any

from watchtower.daemon.backoff import SourceBackoffTracker
from watchtower.daemon.models import DaemonLoopSummary, SourcePollResult
from watchtower.domain.normalized_event import CandidateEvent
from watchtower.graph.runner import GraphRunResult
from watchtower.observability.logging import emit_structured_log
from watchtower.services.app import SessionContext

logger = logging.getLogger(__name__)


class DaemonService:
    """Single-loop pipeline orchestration for enabled ingest sources."""

    def __init__(
        self,
        session: SessionContext,
        *,
        backoff: SourceBackoffTracker | None = None,
    ) -> None:
        self._session = session
        self._backoff = backoff or SourceBackoffTracker()

    def run_once(
        self,
        tenant_id: str,
        *,
        iteration: int = 1,
        ingest_limit: int | None = None,
        pipeline_limit: int = 500,
        graph_limit: int = 100,
    ) -> DaemonLoopSummary:
        started = time.perf_counter()
        settings = self._session.settings
        default_limit = ingest_limit or settings.ingest_default_limit
        mode = self._session.mode_controller.get_mode(tenant_id)
        summary = DaemonLoopSummary(iteration=iteration, tenant_id=tenant_id, mode=mode)

        sources = self._session.sources.list_for_tenant(tenant_id, enabled_only=True)
        for source in sources:
            if self._backoff.is_blocked(source.id):
                summary.sources_skipped_backoff += 1
                summary.source_results.append(
                    SourcePollResult(source_id=source.id, skipped_backoff=True)
                )
                continue

            limit = int(source.config.get("poll_limit", default_limit))
            result = self._session.ingest.ingest_once(tenant_id, source.id, limit=limit)
            self._session.metrics.record_ingest(tenant_id, result)
            poll = SourcePollResult(
                source_id=source.id,
                polled=result.polled,
                stored=result.stored,
                duplicates=result.duplicates,
                error=result.error,
                degraded=result.degraded,
            )
            summary.source_results.append(poll)

            failed = bool(result.error) and result.stored == 0 and result.polled == 0
            if failed:
                delay = self._backoff.record_failure(source.id)
                summary.sources_failed += 1
                summary.errors.append(
                    f"source {source.id}: {result.error} (backoff {delay:.0f}s)"
                )
                emit_structured_log(
                    logger,
                    logging.WARNING,
                    result.error or "ingest failed",
                    tenant_id=tenant_id,
                    source_id=source.id,
                    event_counts={"polled": 0, "stored": 0},
                    extra={"degraded": True},
                )
                continue

            self._backoff.record_success(source.id)
            summary.sources_polled += 1
            summary.raw_stored += result.stored

        pipeline = self._session.pipeline.process_raw_batch(
            tenant_id, limit=pipeline_limit
        )
        self._session.metrics.record_pipeline(
            tenant_id,
            normalized=pipeline.normalized,
            candidates=pipeline.candidates,
        )
        summary.pipeline = {
            "processed": pipeline.processed,
            "normalized": pipeline.normalized,
            "candidates": pipeline.candidates,
            "unknown": pipeline.unknown,
            "skipped": pipeline.skipped,
        }

        pending = self._session.candidate_events.list_pending_graph(
            tenant_id, limit=graph_limit
        )
        for row in pending:
            candidate = self._session.candidate_events.get_by_id(row["id"], tenant_id)
            if candidate is None:
                continue
            graph_result = self._run_graph(candidate)
            summary.graph_runs += 1
            if graph_result.interrupted:
                summary.graph_interrupted += 1
            self._accumulate_graph_outcomes(summary, tenant_id, graph_result)
            alerts_n = self._session.graph.count_alerts(
                tenant_id, graph_result.run_id
            )
            if alerts_n == 0 and graph_result.state.get("alert_id"):
                alerts_n = 1
            self._session.metrics.record_graph_run(
                tenant_id, alerts=alerts_n
            )

        duration_ms = (time.perf_counter() - started) * 1000.0
        self._session.metrics.record_daemon_loop(
            tenant_id, summary, duration_ms=duration_ms
        )
        emit_structured_log(
            logger,
            logging.INFO,
            "daemon loop complete",
            tenant_id=tenant_id,
            event_counts={
                "raw_stored": summary.raw_stored,
                "normalized": int(summary.pipeline.get("normalized", 0)),
                "candidates": int(summary.pipeline.get("candidates", 0)),
                "graph_runs": summary.graph_runs,
                "alerts": summary.alerts_created,
            },
            extra={
                "iteration": iteration,
                "mode": mode,
                "loop_duration_ms": round(duration_ms, 2),
                "sources_failed": summary.sources_failed,
            },
        )
        return summary

    def _run_graph(self, candidate: CandidateEvent) -> GraphRunResult:
        result = self._session.graph_runner.run(candidate)
        if result.interrupted:
            result = self._session.graph_runner.resume(
                result.thread_id, {"decision": "none"}
            )
        return result

    def _accumulate_graph_outcomes(
        self,
        summary: DaemonLoopSummary,
        tenant_id: str,
        result: GraphRunResult,
    ) -> None:
        run_id = result.run_id
        alerts = self._session.graph.count_alerts(tenant_id, run_id)
        silent = self._session.graph.count_silent_findings(tenant_id, run_id)
        learning = self._session.graph.count_learning_events(tenant_id, run_id)
        summary.alerts_created += alerts
        summary.silent_findings += silent
        summary.learning_events += learning
        state = result.state
        if state.get("alert_id") and alerts == 0:
            summary.alerts_created += 1
        if state.get("silent_finding_id") and silent == 0:
            summary.silent_findings += 1
        if state.get("learning_event_id") and learning == 0:
            summary.learning_events += 1
