"""Feedback replay E2E: benign pending rule, approve, scope in/out."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.domain.rules import DecisionContext, RuleScope
from watchtower.e2e.replay import first_candidate_from_feature
from watchtower.e2e.runner import run_graph_to_completion
from tests.graph.conftest import seed_anomaly_baseline, set_tenant_mode


def test_benign_feedback_pending_rule_then_scope_behavior(app, tenant_id, normalizer, extractor):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "run")

    scope = RuleScope(
        user_id="mehmet",
        department_id="backend",
        resource="HR-DB-01",
        action="sql_query",
        feature_id="F-003",
    )
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="expected_behavior",
            actor_id="mgr-1",
            actor_role="manager",
            feature_id="F-003",
            scope=scope,
        )
        assert pending is not None
        stable = session.rules.approve_pending_rule(
            tenant_id,
            pending.id,
            approver_id="sec-1",
            approver_role="security_operator",
        )
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
        out_assess = session.decision.assess(
            __import__(
                "watchtower.decision.service", fromlist=["AssessmentInput"]
            ).AssessmentInput(
                tenant_id=tenant_id,
                feature_id="F-003",
                user_id="yigit",
                department_id="backend",
                resource="HR-DB-01",
                action="sql_query",
                volume=500.0,
                occurred_at=datetime(2026, 5, 23, 10, 0, 0, tzinfo=UTC),
            )
        )

    assert stable.id
    assert in_scope.matched is True
    assert in_scope.downrank is True
    assert out_scope.matched is False
    assert out_assess.should_alert is True
