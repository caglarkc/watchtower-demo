"""Baseline test helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from watchtower.baseline.engine import BaselineEngine
from watchtower.domain.profiles import BehaviorObservation


def seed_metric_series(
    engine: BaselineEngine,
    *,
    tenant_id: str,
    metric_name: str,
    value: float,
    days: int,
    user_id: str,
    department_id: str,
    role_id: str = "engineer",
    seniority: str = "worker",
    end: datetime | None = None,
    daily_jitter: float = 0.0,
) -> None:
    """Insert one observation per day for ``days`` ending at ``end``."""
    anchor = end or datetime.now(UTC)
    start = anchor - timedelta(days=days)
    for offset in range(days):
        observed_at = start + timedelta(days=offset + 1, hours=1)
        if observed_at > anchor:
            observed_at = anchor - timedelta(minutes=1)
        jitter = (offset % 3 - 1) * daily_jitter
        engine.record_observation(
            BehaviorObservation(
                tenant_id=tenant_id,
                metric_name=metric_name,
                value=value + jitter,
                observed_at=observed_at,
                user_id=user_id,
                department_id=department_id,
                role_id=role_id,
                seniority=seniority,  # type: ignore[arg-type]
            )
        )
