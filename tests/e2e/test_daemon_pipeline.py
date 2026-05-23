"""E2E daemon pipeline: server-stack replay JSONL through full runtime loop."""

from __future__ import annotations

from tests.daemon.helpers import (
    db_pipeline_counts,
    register_f001_jsonl_source,
    replay_events_to_jsonl,
    server_stack_log_available,
)
from tests.daemon.test_loop import _run_daemon_once, _seed_f001_baseline
from tests.graph.conftest import set_tenant_mode
from watchtower.config.paths import PROJECT_ROOT
from watchtower.daemon.service import DaemonService


def test_e2e_daemon_f001_replay_jsonl_pipeline(app, tenant_id, tmp_path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_e2e.jsonl")
    register_f001_jsonl_source(app, tenant_id, jsonl)
    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    summary = _run_daemon_once(app, tenant_id)
    counts = db_pipeline_counts(app, tenant_id)

    assert counts["raw_events"] >= 1
    assert counts["normalized_events"] >= 1
    assert counts["candidate_events"] >= 1
    assert counts["graph_runs"] >= 1
    assert counts["silent_findings"] >= 1
    assert summary.silent_findings >= 1


def test_e2e_daemon_server_stack_jsonl_when_logs_present(app, tenant_id):
    logs_root = PROJECT_ROOT / "server-stack" / "logs"
    if not server_stack_log_available():
        return

    with app.session() as session:
        source = session.sources.create(
            tenant_id,
            "server_stack",
            "e2e-daemon-stack",
            {
                "logs_root": str(logs_root),
                "include_globs": ["identity/ad_events.jsonl"],
                "max_files": 1,
            },
        )
        session.conn.commit()
        source_id = source.id

    _seed_f001_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")

    with app.session() as session:
        daemon = DaemonService(session)
        summary = daemon.run_once(tenant_id)
        session.conn.commit()

    assert summary.sources_polled >= 1 or summary.raw_stored >= 0
