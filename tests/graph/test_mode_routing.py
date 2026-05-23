"""Mode routing: learn / run / hybrid."""

from __future__ import annotations

from tests.graph.conftest import make_candidate, seed_anomaly_baseline, set_tenant_mode


def test_learn_mode_no_alert_silent_finding(app, tenant_id):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")
    candidate = make_candidate(tenant_id, volume=500.0)

    with app.session() as session:
        result = session.graph_runner.run(candidate)
        if result.interrupted:
            result = session.graph_runner.resume(
                result.thread_id, {"decision": "none"}
            )
        alerts = session.graph.count_alerts(tenant_id, result.run_id)
        silent = session.graph.count_silent_findings(tenant_id, result.run_id)

    assert alerts == 0
    assert silent == 1
    assert result.state.get("route", {}).get("should_create_alert") is False


def test_run_mode_no_baseline_learning_update(app, tenant_id):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "run")
    candidate = make_candidate(tenant_id, volume=500.0)

    with app.session() as session:
        obs_before = session.conn.execute(
            "SELECT COUNT(*) FROM behavior_observations WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        result = session.graph_runner.run(candidate)
        if result.interrupted:
            result = session.graph_runner.resume(result.thread_id, {"decision": "none"})
        obs_after = session.conn.execute(
            "SELECT COUNT(*) FROM behavior_observations WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        learning = session.graph.count_learning_events(tenant_id, result.run_id)

    assert learning == 0
    assert obs_after == obs_before
    assert result.state.get("route", {}).get("baseline_update_allowed") is False


def test_hybrid_mode_alert_and_controlled_learning(app, tenant_id):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "hybrid")
    candidate = make_candidate(tenant_id, volume=500.0)

    with app.session() as session:
        result = session.graph_runner.run(candidate)
        if result.interrupted:
            result = session.graph_runner.resume(result.thread_id, {"decision": "none"})
        alerts = session.graph.count_alerts(tenant_id, result.run_id)
        learning = session.graph.count_learning_events(tenant_id, result.run_id)

    assert alerts >= 1
    assert learning == 1
    assert result.state.get("route", {}).get("should_enqueue_learning") is True
