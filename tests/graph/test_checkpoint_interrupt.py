"""Checkpoint recovery and approval interrupt."""

from __future__ import annotations

from watchtower.domain.rules import RuleScope
from tests.graph.conftest import make_candidate, seed_anomaly_baseline, set_tenant_mode


def test_checkpoint_recovery_after_interrupt(app, tenant_id):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="false_positive",
            actor_id="mgr-1",
            actor_role="manager",
            feature_id="F-001",
            scope=RuleScope(
                user_id="worker-1",
                feature_id="F-001",
                action="sql_query",
            ),
        )
        assert pending is not None
        candidate = make_candidate(tenant_id, volume=500.0)
        first = session.graph_runner.run(candidate, thread_id="thread-recover-1")
        assert first.interrupted is True
        snap = session.graph_runner.get_state("thread-recover-1")
        assert snap is not None
        assert snap.get("run_id") == first.run_id

        second = session.graph_runner.resume(
            "thread-recover-1",
            {"decision": "approved", "approver_id": "sec-1"},
        )
        assert second.interrupted is False
        assert second.state.get("status") == "completed"
        assert second.state.get("approval_status") == "approved"
        audit = session.graph.list_audit(first.run_id)
        node_names = [a["node_name"] for a in audit]
        assert "await_rule_approval" in node_names
        assert "finalize_decision" in node_names


def test_pending_rule_approval_continues_graph(app, tenant_id):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "hybrid")

    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="expected_behavior",
            actor_id="mgr-2",
            actor_role="manager",
            feature_id="F-001",
            scope=RuleScope(user_id="worker-1", feature_id="F-001"),
        )
        assert pending is not None
        candidate = make_candidate(tenant_id, volume=500.0)
        paused = session.graph_runner.run(candidate)
        assert paused.interrupted
        assert paused.state.get("pending_rule_id") == pending.id

        continued = session.graph_runner.resume(
            paused.thread_id,
            {"decision": "approved", "approver_id": "sec-1"},
        )
        assert continued.state.get("approval_status") == "approved"
        stable = session.rules._repo.list_active_feedback_rules(tenant_id)
        assert len(stable) >= 1


def test_validation_failure_halts_safely(app, tenant_id):
    set_tenant_mode(app, tenant_id, "learn")
    candidate = make_candidate(
        tenant_id,
        extra_attributes={"_force_validation_error": True},
    )
    with app.session() as session:
        result = session.graph_runner.run(candidate)
        run_row = session.graph.get_run(result.run_id)
    assert result.state.get("halted") is True
    assert result.state.get("status") == "failed"
    assert "validation failed" in (result.state.get("error") or "").lower()
    assert run_row is not None
    assert run_row["status"] == "failed"
