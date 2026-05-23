"""Runtime metric names and snapshot model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

METRIC_EVENTS_POLLED = "events_polled_total"
METRIC_RAW_STORED = "raw_events_stored_total"
METRIC_NORMALIZED = "normalized_events_total"
METRIC_CANDIDATES = "candidates_total"
METRIC_GRAPH_RUNS = "graph_runs_total"
METRIC_ALERTS = "alerts_total"
METRIC_SOURCE_ERRORS = "source_errors_total"
METRIC_LLM_CALLS = "llm_calls_total"
METRIC_LOOP_DURATION_COUNT = "loop_duration_ms_count"
METRIC_LOOP_DURATION_SUM = "loop_duration_ms_sum"
METRIC_LOOP_DURATION_LAST = "loop_duration_ms_last"
METRIC_LOOP_DURATION_MAX = "loop_duration_ms_max"

ALL_COUNTERS = (
    METRIC_EVENTS_POLLED,
    METRIC_RAW_STORED,
    METRIC_NORMALIZED,
    METRIC_CANDIDATES,
    METRIC_GRAPH_RUNS,
    METRIC_ALERTS,
    METRIC_SOURCE_ERRORS,
    METRIC_LLM_CALLS,
)


@dataclass
class MetricsSnapshot:
    tenant_id: str
    counters: dict[str, float] = field(default_factory=dict)

    def get(self, name: str, default: float = 0.0) -> float:
        return self.counters.get(name, default)

    @property
    def loop_duration_avg_ms(self) -> float | None:
        count = self.get(METRIC_LOOP_DURATION_COUNT)
        total = self.get(METRIC_LOOP_DURATION_SUM)
        if count <= 0:
            return None
        return total / count

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {"tenant_id": self.tenant_id, "counters": dict(self.counters)}
        avg = self.loop_duration_avg_ms
        if avg is not None:
            out["loop_duration_avg_ms"] = round(avg, 2)
        if METRIC_LOOP_DURATION_LAST in self.counters:
            out["loop_duration_last_ms"] = self.counters[METRIC_LOOP_DURATION_LAST]
        if METRIC_LOOP_DURATION_MAX in self.counters:
            out["loop_duration_max_ms"] = self.counters[METRIC_LOOP_DURATION_MAX]
        return out
