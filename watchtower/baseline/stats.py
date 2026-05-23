"""Statistical helpers for baseline computation."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from statistics import mean, median, pstdev

from watchtower.domain.profiles import MetricStats


def compute_metric_stats(
    metric_name: str,
    values: list[float],
    day_keys: list[str],
) -> MetricStats:
    if not values:
        return MetricStats(metric_name=metric_name)
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    avg = mean(sorted_vals)
    std = pstdev(sorted_vals) if n > 1 else 0.0
    p95_idx = min(n - 1, int(math.ceil(n * 0.95)) - 1)
    return MetricStats(
        metric_name=metric_name,
        sample_count=n,
        distinct_days=len(set(day_keys)),
        mean=avg,
        std=std,
        minimum=sorted_vals[0],
        maximum=sorted_vals[-1],
        p50=median(sorted_vals),
        p95=sorted_vals[p95_idx],
    )


def aggregate_observations(
    rows: list[dict],
) -> dict[str, tuple[list[float], list[str]]]:
    buckets: dict[str, list[tuple[float, str]]] = defaultdict(list)
    for row in rows:
        day_key = row["observed_at"][:10]
        buckets[row["metric_name"]].append((float(row["value"]), day_key))
    return {
        metric: ([v for v, _ in pairs], [d for _, d in pairs])
        for metric, pairs in buckets.items()
    }


def profile_confidence(
    metrics: dict[str, MetricStats],
    *,
    window_days: int,
) -> float:
    if not metrics:
        return 0.0
    per_metric: list[float] = []
    for stats in metrics.values():
        if stats.sample_count == 0:
            continue
        coverage = min(1.0, stats.distinct_days / max(window_days, 1))
        volume = min(1.0, stats.sample_count / max(window_days // 2, 1))
        per_metric.append(coverage * 0.6 + volume * 0.4)
    if not per_metric:
        return 0.0
    return round(sum(per_metric) / len(per_metric), 4)
