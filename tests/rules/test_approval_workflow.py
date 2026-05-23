"""Pending rule approval workflow."""

from __future__ import annotations

from datetime import UTC, datetime

from watchtower.domain.rules import DecisionContext, RuleScope


def _ctx(**kwargs: object) -> DecisionContext:
    defaults = {
        "tenant_id": "",
        "feature_id": "F-001",
        "user_id": "mehmet",
        "department_id": "backend",
        "resource": "HR-DB-01",
        "action": "sql_query",
        "occurred_at": datetime(2026, 5, 23, 3, 0, 0, tzinfo=UTC),
        "detection_class": "baseline-anomaly",
    }
    defaults.update(kwargs)
    return DecisionContext(**defaults)  # type: ignore[arg-type]


def test_pending_rule_not_applied_until_approved(app, tenant_id):
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="false_positive",
            actor_id="mgr-1",
            actor_role="manager",
            feature_id="F-001",
            scope=RuleScope(
                user_id="mehmet",
                department_id="backend",
                resource="HR-DB-01",
                action="sql_query",
            ),
        )
        assert pending is not None
        before = session.rules.apply_feedback_rules(
            _ctx(tenant_id=tenant_id)
        )
        stable = session.rules.approve_pending_rule(
            tenant_id,
            pending.id,
            approver_id="sec-1",
            approver_role="security_operator",
        )
        after = session.rules.apply_feedback_rules(_ctx(tenant_id=tenant_id))

    assert before.matched is True
    assert before.suppress_alert is False
    assert before.reason == "pending_rule_not_approved"
    assert after.matched is True
    assert after.downrank is True
    assert after.applied_rule_id == stable.id


def test_rejected_pending_never_becomes_stable(app, tenant_id):
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="expected_behavior",
            actor_id="mgr-2",
            actor_role="manager",
            feature_id="F-002",
            scope=RuleScope(user_id="ali", action="file_read"),
        )
        assert pending is not None
        session.rules.reject_pending_rule(
            tenant_id,
            pending.id,
            approver_id="admin-1",
            approver_role="system_admin",
            comment="Insufficient evidence",
        )
        result = session.rules.apply_feedback_rules(
            _ctx(
                tenant_id=tenant_id,
                feature_id="F-002",
                user_id="ali",
                action="file_read",
            )
        )
        approvals = session.rules._repo.list_rule_approvals(tenant_id, pending.id)

    assert result.matched is False
    assert len(approvals) == 1
    assert approvals[0].decision == "rejected"
