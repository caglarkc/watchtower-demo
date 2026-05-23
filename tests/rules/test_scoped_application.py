"""Scoped feedback rules: downrank in-scope, alert out-of-scope."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from watchtower.domain.rules import DecisionContext, RuleScope


def _approve_rule(app, tenant_id: str, scope: RuleScope, feature_id: str = "F-003"):
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
        stable = session.rules.approve_pending_rule(
            tenant_id,
            pending.id,
            approver_id="sec-1",
            approver_role="security_operator",
        )
        return stable


def test_approved_rule_downranks_in_scope(app, tenant_id):
    scope = RuleScope(
        user_id="mehmet",
        department_id="backend",
        resource="HR-DB-01",
        action="sql_query",
        feature_id="F-003",
    )
    _approve_rule(app, tenant_id, scope)

    with app.session() as session:
        in_scope = session.rules.apply_feedback_rules(
            DecisionContext(
                tenant_id=tenant_id,
                feature_id="F-003",
                user_id="mehmet",
                department_id="backend",
                resource="HR-DB-01",
                action="sql_query",
                occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
                detection_class="baseline-anomaly",
            )
        )
        out_scope = session.rules.apply_feedback_rules(
            DecisionContext(
                tenant_id=tenant_id,
                feature_id="F-003",
                user_id="yigit",
                department_id="backend",
                resource="HR-DB-01",
                action="sql_query",
                occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
                detection_class="baseline-anomaly",
            )
        )

    assert in_scope.matched is True
    assert in_scope.downrank is True
    assert in_scope.severity_delta < 0

    assert out_scope.matched is False
    assert out_scope.downrank is False


def test_expired_feedback_rule_not_applied(app, tenant_id):
    scope = RuleScope(user_id="temp-user", feature_id="F-004", action="export")
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="temporary_exception",
            actor_id="mgr-1",
            actor_role="manager",
            feature_id="F-004",
            scope=scope,
            expires_in_days=1,
        )
        assert pending is not None
        stable = session.rules.approve_pending_rule(
            tenant_id,
            pending.id,
            approver_id="sec-1",
            approver_role="security_operator",
        )
        expired_at = (stable.expires_at or datetime.now(UTC)) + timedelta(seconds=1)
        active = session.rules.apply_feedback_rules(
            DecisionContext(
                tenant_id=tenant_id,
                feature_id="F-004",
                user_id="temp-user",
                action="export",
                occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
            ),
            as_of=expired_at,
        )

    assert active.matched is False
