"""Structured logging, runtime metrics, and production readiness helpers."""

from watchtower.observability.logging import emit_structured_log
from watchtower.observability.metrics import (
    METRIC_ALERTS,
    METRIC_CANDIDATES,
    METRIC_EVENTS_POLLED,
    METRIC_GRAPH_RUNS,
    METRIC_LLM_CALLS,
    METRIC_LOOP_DURATION_LAST,
    METRIC_LOOP_DURATION_MAX,
    METRIC_LOOP_DURATION_SUM,
    METRIC_NORMALIZED,
    METRIC_RAW_STORED,
    METRIC_SOURCE_ERRORS,
    MetricsSnapshot,
)
from watchtower.observability.service import MetricsService

__all__ = [
    "METRIC_ALERTS",
    "METRIC_CANDIDATES",
    "METRIC_EVENTS_POLLED",
    "METRIC_GRAPH_RUNS",
    "METRIC_LLM_CALLS",
    "METRIC_LOOP_DURATION_LAST",
    "METRIC_LOOP_DURATION_MAX",
    "METRIC_LOOP_DURATION_SUM",
    "METRIC_NORMALIZED",
    "METRIC_RAW_STORED",
    "METRIC_SOURCE_ERRORS",
    "MetricsService",
    "MetricsSnapshot",
    "emit_structured_log",
]
