"""Policy-rule feedback must not auto-suppress without explicit approval."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.domain.rules import DecisionContext, RuleScope


def test_policy_rule_feedback_requires_explicit_suppression_approval(app, tenant_id):
    scope = RuleScope(
        user_id="frontend-dev",
        department_id="engineering",
        resource="PROD-DB-01",
        action="direct_sql",
        feature_id="F-010",
    )
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="false_positive",
            actor_id="mgr-1",
            actor_role="manager",
            feature_id="F-010",
            scope=scope,
        )
        assert pending is not None
        assert pending.requires_policy_suppression_approval is True
        assert pending.effect.suppress_alert is False

        stable_plain = session.rules.approve_pending_rule(
            tenant_id,
            pending.id,
            approver_id="sec-1",
            approver_role="security_operator",
            allow_policy_suppression=False,
        )
        plain_result = session.rules.apply_feedback_rules(
            DecisionContext(
                tenant_id=tenant_id,
                feature_id="F-010",
                user_id="frontend-dev",
                department_id="engineering",
                resource="PROD-DB-01",
                action="direct_sql",
                occurred_at=datetime(2026, 5, 23, 12, 0, 0, tzinfo=UTC),
                detection_class="policy-rule",
            )
        )

    assert plain_result.matched is True
    assert plain_result.suppress_alert is False
    assert plain_result.policy_suppression_blocked is True

    with app.session() as session:
        _, pending2 = session.feedback.submit_feedback(
            tenant_id,
            kind="false_positive",
            actor_id="mgr-2",
            actor_role="manager",
            feature_id="F-010",
            scope=RuleScope(
                user_id="frontend-dev-2",
                resource="PROD-DB-02",
                action="direct_sql",
                feature_id="F-010",
            ),
        )
        assert pending2 is not None
        session.rules.approve_pending_rule(
            tenant_id,
            pending2.id,
            approver_id="sec-1",
            approver_role="security_operator",
            allow_policy_suppression=True,
        )
        explicit = session.rules.apply_feedback_rules(
            DecisionContext(
                tenant_id=tenant_id,
                feature_id="F-010",
                user_id="frontend-dev-2",
                resource="PROD-DB-02",
                action="direct_sql",
                occurred_at=datetime(2026, 5, 23, 12, 0, 0, tzinfo=UTC),
                detection_class="policy-rule",
            )
        )

    assert explicit.suppress_alert is True
    assert explicit.policy_suppression_blocked is False
