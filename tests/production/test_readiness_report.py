"""Production readiness JSON includes metrics evidence."""

from __future__ import annotations

from watchtower.daemon.service import DaemonService
from watchtower.e2e.soak import (
    register_f001_jsonl_source,
    replay_events_to_jsonl,
    seed_f001_baseline,
)
from watchtower.observability.readiness import build_production_readiness_report
from tests.graph.conftest import set_tenant_mode


def test_readiness_report_includes_metrics_and_soak(prod_app, bootstrapped_tenant, tmp_path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_ready.jsonl")
    register_f001_jsonl_source(
        prod_app, bootstrapped_tenant, jsonl, source_id="src-ready"
    )
    seed_f001_baseline(prod_app, bootstrapped_tenant)
    set_tenant_mode(prod_app, bootstrapped_tenant, "learn")
    with prod_app.session() as session:
        DaemonService(session).run_once(bootstrapped_tenant)
        session.conn.commit()
        report = build_production_readiness_report(
            conn=session.conn,
            settings=prod_app.settings,
            session=session,
            metrics=session.metrics,
            tenant_id=bootstrapped_tenant,
            soak_summary={"label": "test", "passed": True},
        )
    assert report["metrics"] is not None
    assert report["metrics"]["counters"]["raw_events_stored_total"] >= 1
    assert report["soak"]["passed"] is True
    assert report["health"]["status"] in ("healthy", "degraded")
