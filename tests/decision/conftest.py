"""Decision test helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.domain.assessment import AssessmentInput
from watchtower.domain.rules import RuleScope
from watchtower.services.app import AppContext
from tests.baseline.conftest import seed_metric_series


def assessment_input(
    tenant_id: str,
    *,
    feature_id: str = "F-001",
    user_id: str = "user-1",
    department_id: str = "backend",
    role_id: str = "engineer",
    seniority: str = "worker",
    resource: str = "HR-DB-01",
    action: str = "sql_query",
    volume: float = 100.0,
    metric_name: str = "sql_query_count",
    related_signals: list[str] | None = None,
) -> AssessmentInput:
    return AssessmentInput(
        tenant_id=tenant_id,
        feature_id=feature_id,
        user_id=user_id,
        department_id=department_id,
        role_id=role_id,
        seniority=seniority,
        resource=resource,
        action=action,
        volume=volume,
        metric_name=metric_name,
        occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
        related_signals=related_signals or [],
    )


def seed_user_baseline(
    app: AppContext,
    tenant_id: str,
    *,
    user_id: str,
    value: float,
    days: int = 30,
    department_id: str = "backend",
    role_id: str = "engineer",
    seniority: str = "worker",
    metric_name: str = "sql_query_count",
) -> None:
    with app.session() as session:
        seed_metric_series(
            session.baseline,
            tenant_id=tenant_id,
            metric_name=metric_name,
            value=value,
            days=days,
            user_id=user_id,
            department_id=department_id,
            role_id=role_id,
            seniority=seniority,
        )
        session.baseline.rebuild_profiles(tenant_id, window_days=45)


def approve_feedback_rule(
    app: AppContext,
    tenant_id: str,
    scope: RuleScope,
    *,
    feature_id: str,
    allow_policy_suppression: bool = False,
) -> None:
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="false_positive",
            actor_id="mgr-1",
            actor_role="manager",
            feature_id=feature_id,
            scope=scope,
        )
        assert pending is not None
        session.rules.approve_pending_rule(
            tenant_id,
            pending.id,
            approver_id="sec-1",
            approver_role="security_operator",
            allow_policy_suppression=allow_policy_suppression,
        )
