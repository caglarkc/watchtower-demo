"""Short soak: real daemon loop + metrics growth (not sleep-only)."""

from __future__ import annotations

from watchtower.daemon.service import DaemonService
from watchtower.e2e.soak import (
    db_pipeline_counts,
    register_f001_jsonl_source,
    replay_events_to_jsonl,
    seed_f001_baseline,
)
from watchtower.health.service import HealthService
from watchtower.observability.metrics import (
    METRIC_GRAPH_RUNS,
    METRIC_LOOP_DURATION_COUNT,
    METRIC_RAW_STORED,
)
from tests.graph.conftest import set_tenant_mode


def test_short_soak_daemon_pipeline_and_metrics(prod_app, bootstrapped_tenant, tmp_path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_soak.jsonl")
    register_f001_jsonl_source(
        prod_app, bootstrapped_tenant, jsonl, source_id="src-soak"
    )
    seed_f001_baseline(prod_app, bootstrapped_tenant)
    set_tenant_mode(prod_app, bootstrapped_tenant, "learn")

    iterations = 3
    for _ in range(iterations):
        with prod_app.session() as session:
            DaemonService(session).run_once(bootstrapped_tenant)
            session.conn.commit()

    counts = db_pipeline_counts(prod_app, bootstrapped_tenant)
    with prod_app.session() as session:
        snap = session.metrics.snapshot(bootstrapped_tenant)
        report = HealthService().run(
            conn=session.conn,
            settings=prod_app.settings,
            session=session,
        )

    assert counts["raw_events"] >= 1
    assert counts["normalized_events"] >= 1
    assert counts["graph_runs"] >= 1
    assert snap.get(METRIC_RAW_STORED) >= 1
    assert snap.get(METRIC_GRAPH_RUNS) >= 1
    assert snap.get(METRIC_LOOP_DURATION_COUNT) >= iterations
    assert report.status in ("healthy", "degraded")
    metric_check = next(c for c in report.checks if c.name == "metrics")
    assert metric_check.details.get("counters")
