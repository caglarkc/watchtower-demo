"""Policy-rule guard E2E: no silent normalization without explicit approval."""

from __future__ import annotations

from watchtower.domain.rules import RuleScope
from tests.decision.conftest import approve_feedback_rule, assessment_input


def test_policy_rule_not_auto_normalized_without_approval(app, tenant_id):
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
