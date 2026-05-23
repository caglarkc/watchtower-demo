"""Durable SQLite checkpoint + process restart resume."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver

from watchtower.config.settings import DEFAULT_SETTINGS, WatchtowerSettings
from watchtower.domain.rules import RuleScope
from watchtower.graph.checkpointing import GraphCheckpointStore, prune_completed_checkpoints
from watchtower.graph.resume import GraphResumeService
from watchtower.services.app import create_app
from tests.graph.conftest import make_candidate, seed_anomaly_baseline, set_tenant_mode


def test_production_default_is_durable_not_memory():
    store = GraphCheckpointStore.from_settings(DEFAULT_SETTINGS)
    saver = store.get_checkpointer()
    assert not isinstance(saver, MemorySaver)
    assert isinstance(saver, SqliteSaver)
    assert DEFAULT_SETTINGS.graph_checkpoint_use_memory is False
    assert DEFAULT_SETTINGS.graph_checkpoint_enabled is True


def test_durable_checkpoint_survives_new_app_instance(app, tenant_id, settings):
    """Second app/runner instance must reload checkpoint from disk."""
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    thread_id = "thread-durable-restart"
    run_id: str | None = None

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
        first = session.graph_runner.run(candidate, thread_id=thread_id)
        run_id = first.run_id
        session.conn.commit()

    assert first.interrupted is True
    assert app.checkpoint_store.thread_has_checkpoint(thread_id)

    app2 = create_app(settings=settings, database_path=settings.database_path)
    assert app2.checkpoint_store.thread_has_checkpoint(thread_id)

    with app2.session() as session:
        assert session.graph_runner.checkpoint_exists(thread_id)
        snap = session.graph_runner.get_state(thread_id)
        assert snap is not None
        assert snap.get("run_id") == run_id

        svc = GraphResumeService(session, app2.checkpoint_store)
        second = svc.resume(
            tenant_id,
            thread_id,
            {"decision": "approved", "approver_id": "sec-1"},
        )
        session.conn.commit()

    assert second.interrupted is False
    assert second.state.get("status") == "completed"
    assert second.state.get("approval_status") == "approved"

    with app2.session() as session:
        audit = session.graph.list_audit(run_id)
        node_names = [a["node_name"] for a in audit]
        assert "await_rule_approval" in node_names
        assert "finalize_decision" in node_names
        assert "checkpoint_meta" in node_names
        stable = session.rules._repo.list_active_feedback_rules(tenant_id)
        assert len(stable) >= 1
        row = session.graph.get_run(run_id)
        assert row is not None
        assert row["thread_id"] == thread_id
        assert int(row["interrupted"]) == 0


def test_checkpoint_retention_prunes_old_completed(app, tenant_id, settings):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")
    thread_id = "thread-retention-old"

    with app.session() as session:
        candidate = make_candidate(tenant_id, volume=10.0)
        result = session.graph_runner.run(candidate, thread_id=thread_id)
        if result.interrupted:
            result = session.graph_runner.resume(
                thread_id, {"decision": "none"}
            )
        old_finished = (datetime.now(UTC) - timedelta(days=60)).isoformat()
        session.conn.execute(
            """
            UPDATE graph_runs SET status = 'completed', finished_at = ?, interrupted = 0
            WHERE id = ?
            """,
            (old_finished, result.run_id),
        )
        session.conn.commit()

    assert app.checkpoint_store.thread_has_checkpoint(thread_id)

    with app.session() as session:
        removed = prune_completed_checkpoints(
            session.conn,
            app.checkpoint_store,
            retention_days=30,
        )
        session.conn.commit()

    assert removed >= 1
    assert not app.checkpoint_store.thread_has_checkpoint(thread_id)
