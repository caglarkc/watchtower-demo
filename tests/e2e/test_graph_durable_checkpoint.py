"""E2E: durable checkpoint + approval resume across app restart."""

from __future__ import annotations

from watchtower.domain.rules import RuleScope
from watchtower.graph.resume import GraphResumeService
from watchtower.services.app import create_app
from tests.graph.conftest import make_candidate, seed_anomaly_baseline, set_tenant_mode


def test_e2e_pending_rule_approval_resume_after_restart(app, tenant_id, settings):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "hybrid")
    thread_id = "e2e-thread-approval-resume"

    with app.session() as session:
        _, pending = session.feedback.submit_feedback(
            tenant_id,
            kind="expected_behavior",
            actor_id="mgr-e2e",
            actor_role="manager",
            feature_id="F-001",
            scope=RuleScope(user_id="worker-1", feature_id="F-001"),
        )
        assert pending is not None
        candidate = make_candidate(tenant_id, volume=500.0)
        paused = session.graph_runner.run(candidate, thread_id=thread_id)
        session.conn.commit()

    assert paused.interrupted
    assert paused.state.get("pending_rule_id") == pending.id
    assert app.checkpoint_store.thread_has_checkpoint(thread_id)

    app2 = create_app(settings=settings, database_path=settings.database_path)
    with app2.session() as session:
        interrupted = GraphResumeService(session, app2.checkpoint_store).list_interrupted(
            tenant_id
        )
        assert any(r.thread_id == thread_id for r in interrupted)

        continued = GraphResumeService(session, app2.checkpoint_store).resume(
            tenant_id,
            thread_id,
            {"decision": "approved", "approver_id": "sec-e2e"},
        )
        session.conn.commit()

    assert continued.state.get("approval_status") == "approved"
    assert continued.state.get("status") == "completed"

    with app2.session() as session:
        stable = session.rules._repo.list_active_feedback_rules(tenant_id)
        assert len(stable) >= 1
        audit = session.graph.list_audit(paused.run_id)
        assert any(a["node_name"] == "finalize_decision" for a in audit)
