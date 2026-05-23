"""Daemon loop integration tests (server-stack replay JSONL)."""

from __future__ import annotations

from tests.daemon.helpers import db_pipeline_counts, register_f001_jsonl_source, replay_events_to_jsonl
from tests.e2e.conftest import seed_baseline_for_candidate
from tests.graph.conftest import set_tenant_mode
from watchtower.daemon.service import DaemonService


def _run_daemon_once(app, tenant_id):
    with app.session() as session:
        daemon = DaemonService(session)
        summary = daemon.run_once(tenant_id)
        session.conn.commit()
        return summary


def _seed_f001_baseline(app, tenant_id):
    from watchtower.e2e.soak import seed_f001_baseline

    seed_f001_baseline(app, tenant_id)


def test_daemon_pipeline_raw_to_graph_chain(app, tenant_id, f001_source):
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    summary = _run_daemon_once(app, tenant_id)
    counts = db_pipeline_counts(app, tenant_id)

    assert summary.raw_stored >= 1
    assert counts["raw_events"] >= 1
    assert counts["normalized_events"] >= 1
    assert counts["candidate_events"] >= 1
    assert counts["graph_runs"] >= 1
    assert summary.graph_runs >= 1


def test_learn_mode_daemon_zero_alert_silent_and_learning(app, tenant_id, f001_source):
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    summary = _run_daemon_once(app, tenant_id)
    counts = db_pipeline_counts(app, tenant_id)

    assert counts["alerts"] == 0
    assert counts["silent_findings"] >= 1
    assert counts["learning_events"] >= 1
    assert summary.alerts_created == 0
    assert summary.silent_findings >= 1
    assert summary.learning_events >= 1


def test_run_mode_daemon_alert_no_learning(app, tenant_id, f001_source):
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "run")

    with app.session() as session:
        obs_before = session.conn.execute(
            "SELECT COUNT(*) FROM behavior_observations WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]

    summary = _run_daemon_once(app, tenant_id)
    counts = db_pipeline_counts(app, tenant_id)

    with app.session() as session:
        obs_after = session.conn.execute(
            "SELECT COUNT(*) FROM behavior_observations WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]

    assert counts["learning_events"] == 0
    assert summary.learning_events == 0
    assert obs_after == obs_before
    assert counts["alerts"] >= 1 or summary.alerts_created >= 1


def test_hybrid_mode_daemon_alert_and_learning(app, tenant_id, f001_source):
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "hybrid")

    summary = _run_daemon_once(app, tenant_id)
    counts = db_pipeline_counts(app, tenant_id)

    assert counts["alerts"] >= 1
    assert counts["learning_events"] >= 1
    assert summary.alerts_created >= 1
    assert summary.learning_events >= 1


def test_daemon_cursor_no_duplicate_raw_on_rerun(app, tenant_id, f001_jsonl):
    register_f001_jsonl_source(app, tenant_id, f001_jsonl)
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    first = _run_daemon_once(app, tenant_id)
    second = _run_daemon_once(app, tenant_id)
    counts = db_pipeline_counts(app, tenant_id)

    assert first.raw_stored >= 1
    assert second.raw_stored == 0
    assert counts["raw_events"] == first.raw_stored


def test_one_source_fail_other_continues(app, tenant_id, f001_jsonl):
    register_f001_jsonl_source(app, tenant_id, f001_jsonl, source_id="src-good")
    with app.session() as session:
        session.sources.create(
            tenant_id,
            "mock",
            "failing",
            config={"events": [], "fail_health": True},
            source_id="src-bad",
        )
        session.conn.commit()

    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    summary = _run_daemon_once(app, tenant_id)

    assert summary.sources_failed >= 1
    assert summary.sources_polled >= 1
    assert summary.raw_stored >= 1
    counts = db_pipeline_counts(app, tenant_id)
    assert counts["raw_events"] >= 1
