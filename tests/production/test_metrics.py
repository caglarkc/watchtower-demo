"""Runtime metrics from real daemon pipeline."""

from __future__ import annotations

from watchtower.daemon.service import DaemonService
from watchtower.e2e.soak import (
    db_pipeline_counts,
    register_f001_jsonl_source,
    replay_events_to_jsonl,
    seed_f001_baseline,
)
from watchtower.observability.metrics import (
    METRIC_CANDIDATES,
    METRIC_EVENTS_POLLED,
    METRIC_GRAPH_RUNS,
    METRIC_LOOP_DURATION_LAST,
    METRIC_NORMALIZED,
    METRIC_RAW_STORED,
)
from tests.graph.conftest import set_tenant_mode


def test_daemon_increments_runtime_metrics(prod_app, bootstrapped_tenant, tmp_path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_metrics.jsonl")
    register_f001_jsonl_source(
        prod_app, bootstrapped_tenant, jsonl, source_id="src-metrics"
    )
    seed_f001_baseline(prod_app, bootstrapped_tenant)
    set_tenant_mode(prod_app, bootstrapped_tenant, "learn")

    with prod_app.session() as session:
        summary = DaemonService(session).run_once(bootstrapped_tenant)
        session.conn.commit()
        snap = session.metrics.snapshot(bootstrapped_tenant)

    counts = db_pipeline_counts(prod_app, bootstrapped_tenant)
    assert counts["raw_events"] >= 1
    assert counts["graph_runs"] >= 1
    assert summary.raw_stored >= 1
    assert snap.get(METRIC_EVENTS_POLLED) >= 1
    assert snap.get(METRIC_RAW_STORED) >= 1
    assert snap.get(METRIC_NORMALIZED) >= 1
    assert snap.get(METRIC_CANDIDATES) >= 1
    assert snap.get(METRIC_GRAPH_RUNS) >= 1
    assert snap.get(METRIC_LOOP_DURATION_LAST) > 0


def test_cli_metrics_json(prod_app, bootstrapped_tenant, tmp_path):
    from typer.testing import CliRunner

    from watchtower.cli.main import app as cli_app

    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_cli_metrics.jsonl")
    register_f001_jsonl_source(
        prod_app, bootstrapped_tenant, jsonl, source_id="src-cli-metrics"
    )
    seed_f001_baseline(prod_app, bootstrapped_tenant)
    set_tenant_mode(prod_app, bootstrapped_tenant, "learn")

    with prod_app.session() as session:
        DaemonService(session).run_once(bootstrapped_tenant)
        session.conn.commit()

    db = str(prod_app.settings.database_path)
    runner = CliRunner()
    result = runner.invoke(cli_app, ["--db", db, "metrics", "--json"])
    assert result.exit_code == 0
    assert METRIC_RAW_STORED in result.stdout
