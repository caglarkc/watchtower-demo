"""End-to-end decision scenarios via DecisionService."""

from __future__ import annotations

from watchtower.domain.assessment import SEVERITY_ORDER
from watchtower.domain.rules import RuleScope
from tests.decision.conftest import (
    approve_feedback_rule,
    assessment_input,
    seed_user_baseline,
)


def test_frontend_direct_db_access_critical_via_decision(app, tenant_id):
    with app.session() as session:
        result = session.decision.assess(
            assessment_input(
                tenant_id,
                feature_id="F-010",
                user_id="dev-1",
                role_id="frontend",
                department_id="engineering",
                resource="PROD-DB-01",
                action="direct_sql",
                volume=1.0,
            )
        )
    assert result.policy_violated is True
    assert result.severity == "CRITICAL"
    assert result.should_alert is True
    assert len(result.breakdown.components) >= 1


def test_high_volume_user_within_baseline_no_alert(app, tenant_id):
    seed_user_baseline(
        app,
        tenant_id,
        user_id="mehmet",
        value=1000.0,
        department_id="backend",
    )
    with app.session() as session:
        result = session.decision.assess(
            assessment_input(
                tenant_id,
                user_id="mehmet",
                volume=1000.0,
                metric_name="sql_query_count",
            )
        )
    assert result.baseline_anomaly is False
    assert result.should_alert is False
    assert SEVERITY_ORDER[result.severity] <= SEVERITY_ORDER["WARNING"]


def test_high_volume_user_downranked_with_approved_feedback(app, tenant_id):
    seed_user_baseline(
        app,
        tenant_id,
        user_id="yigit",
        value=10.0,
    )
    approve_feedback_rule(
        app,
        tenant_id,
        RuleScope(
            user_id="yigit",
            feature_id="F-001",
            action="sql_query",
        ),
        feature_id="F-001",
    )
    with app.session() as session:
        result = session.decision.assess(
            assessment_input(
                tenant_id,
                user_id="yigit",
                volume=100.0,
            )
        )
    assert result.feedback_applied is True
    assert result.should_alert is False
    assert result.breakdown.downranked or result.severity in ("LOG", "WARNING")


def test_manager_and_worker_different_severity_same_volume(app, tenant_id):
    seed_user_baseline(
        app,
        tenant_id,
        user_id="worker-1",
        value=10.0,
        role_id="engineer",
        seniority="worker",
    )
    seed_user_baseline(
        app,
        tenant_id,
        user_id="mgr-1",
        value=500.0,
        role_id="engineering_manager",
        seniority="manager",
    )
    with app.session() as session:
        worker = session.decision.assess(
            assessment_input(
                tenant_id,
                user_id="worker-1",
                role_id="engineer",
                seniority="worker",
                volume=100.0,
            )
        )
        manager = session.decision.assess(
            assessment_input(
                tenant_id,
                user_id="mgr-1",
                role_id="engineering_manager",
                seniority="manager",
                volume=100.0,
            )
        )
    assert worker.baseline_anomaly is True
    assert manager.baseline_anomaly is False
    assert SEVERITY_ORDER[worker.severity] > SEVERITY_ORDER[manager.severity]


def test_manager_personal_baseline_deviation_still_alerts(app, tenant_id):
    seed_user_baseline(
        app,
        tenant_id,
        user_id="mgr-strict",
        value=50.0,
        role_id="engineering_manager",
        seniority="manager",
    )
    with app.session() as session:
        result = session.decision.assess(
            assessment_input(
                tenant_id,
                user_id="mgr-strict",
                role_id="engineering_manager",
                seniority="manager",
                volume=500.0,
            )
        )
    assert result.baseline_anomaly is True
    assert result.should_alert is True
    assert SEVERITY_ORDER[result.severity] >= SEVERITY_ORDER["ALERT"]


def test_cross_signal_raises_severity(app, tenant_id):
    with app.session() as session:
        single = session.decision.assess(
            assessment_input(
                tenant_id,
                feature_id="F-009",
                volume=50.0,
                related_signals=[],
            )
        )
        multi = session.decision.assess(
            assessment_input(
                tenant_id,
                feature_id="F-009",
                volume=50.0,
                related_signals=["F-001", "F-002"],
            )
        )
    assert multi.correlation_boost is True
    assert SEVERITY_ORDER[multi.severity] >= SEVERITY_ORDER[single.severity]
    corr_pts = [
        c.points
        for c in multi.breakdown.components
        if c.source == "correlation"
    ]
    assert corr_pts and corr_pts[0] > 0


def test_policy_rule_not_suppressed_without_explicit_approval(app, tenant_id):
    approve_feedback_rule(
        app,
        tenant_id,
        RuleScope(
            user_id="dev-1",
            feature_id="F-010",
            resource="PROD-DB-01",
            action="direct_sql",
        ),
        feature_id="F-010",
        allow_policy_suppression=False,
    )
    with app.session() as session:
        result = session.decision.assess(
            assessment_input(
                tenant_id,
                feature_id="F-010",
                user_id="dev-1",
                role_id="frontend",
                resource="PROD-DB-01",
                action="direct_sql",
                volume=1.0,
            )
        )
    assert result.policy_violated is True
    assert result.breakdown.policy_suppression_blocked is True
    assert result.should_alert is True
    assert result.severity == "CRITICAL"


def test_score_breakdown_never_empty(app, tenant_id):
    with app.session() as session:
        result = session.decision.assess(
            assessment_input(tenant_id, feature_id="F-002", volume=5.0)
        )
    assert len(result.breakdown.components) >= 1
    assert result.breakdown.final_severity == result.severity
    sources = {c.source for c in result.breakdown.components}
    assert sources  # non-empty explainable components
