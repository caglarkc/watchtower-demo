"""Manager feedback must create pending_rule, never stable rule."""

from __future__ import annotations

from watchtower.domain.rules import RuleScope


def test_manager_feedback_creates_pending_rule_not_stable(app, tenant_id):
    with app.session() as session:
        event, pending = session.feedback.submit_feedback(
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
            comment="Expected nightly batch",
        )
        stable_rules = session.rules._repo.list_active_feedback_rules(tenant_id)
        pending_list = session.rules._repo.list_pending_rules(tenant_id)

    assert pending is not None
    assert pending.status == "pending"
    assert pending.feedback_event_id == event.id
    assert pending.proposed_role == "manager"
    assert len(pending_list) == 1
    assert len(stable_rules) == 0


def test_true_positive_feedback_does_not_create_pending(app, tenant_id):
    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="true_positive",
            actor_id="op-1",
            actor_role="operator",
            feature_id="F-001",
        )
        pending_list = session.rules._repo.list_pending_rules(tenant_id)

    assert pending is None
    assert len(pending_list) == 0
