"""Graph test helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.domain.normalized_event import CandidateEvent
from watchtower.services.app import AppContext
from tests.baseline.conftest import seed_metric_series


def make_candidate(
    tenant_id: str,
    *,
    feature_id: str = "F-001",
    user_id: str = "worker-1",
    department_id: str = "backend",
    role_id: str = "engineer",
    seniority: str = "worker",
    resource: str = "HR-DB-01",
    action: str = "sql_query",
    volume: float = 500.0,
    metric_name: str = "sql_query_count",
    extra_attributes: dict | None = None,
) -> CandidateEvent:
    attrs = {
        "user_id": user_id,
        "department_id": department_id,
        "role_id": role_id,
        "seniority": seniority,
        "volume": volume,
        "metric_name": metric_name,
    }
    if extra_attributes:
        attrs.update(extra_attributes)
    return CandidateEvent(
        tenant_id=tenant_id,
        normalized_event_id="norm-1",
        feature_hint=feature_id,
        actor=user_id,
        action=action,
        resource=resource,
        occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
        attributes=attrs,
    )


def seed_anomaly_baseline(
    app: AppContext,
    tenant_id: str,
    *,
    user_id: str = "worker-1",
    normal_value: float = 10.0,
) -> None:
    with app.session() as session:
        seed_metric_series(
            session.baseline,
            tenant_id=tenant_id,
            metric_name="sql_query_count",
            value=normal_value,
            days=30,
            user_id=user_id,
            department_id="backend",
        )
        session.baseline.rebuild_profiles(tenant_id, window_days=45)


def set_tenant_mode(app: AppContext, tenant_id: str, mode: str) -> None:
    with app.session() as session:
        session.mode_controller.set_mode(tenant_id, mode)  # type: ignore[arg-type]
