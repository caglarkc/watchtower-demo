"""Source outage: health degraded while daemon loop continues."""

from __future__ import annotations

from watchtower.daemon.service import DaemonService
from watchtower.e2e.soak import (
    register_f001_jsonl_source,
    replay_events_to_jsonl,
    seed_f001_baseline,
)
from watchtower.health.service import HealthService
from watchtower.observability.metrics import METRIC_SOURCE_ERRORS
from tests.graph.conftest import set_tenant_mode


def test_outage_degrades_health_daemon_continues(prod_app, bootstrapped_tenant, tmp_path):
    good = replay_events_to_jsonl("F-001", tmp_path / "good.jsonl")
    register_f001_jsonl_source(
        prod_app, bootstrapped_tenant, good, source_id="src-good"
    )
    with prod_app.session() as session:
        session.sources.create(
            bootstrapped_tenant,
            "mock",
            "failing",
            config={"events": [], "fail_health": True},
            source_id="src-bad",
        )
        session.conn.commit()

    seed_f001_baseline(prod_app, bootstrapped_tenant)
    set_tenant_mode(prod_app, bootstrapped_tenant, "learn")

    with prod_app.session() as session:
        summary = DaemonService(session).run_once(bootstrapped_tenant)
        session.conn.commit()
        health = HealthService().run(
            conn=session.conn,
            settings=prod_app.settings,
            session=session,
        )
        snap = session.metrics.snapshot(bootstrapped_tenant)

    assert summary.sources_polled >= 1
    assert summary.raw_stored >= 1
    assert snap.get(METRIC_SOURCE_ERRORS) >= 1
    statuses = {c.name: c.status for c in health.checks}
    assert statuses.get("sources") in ("degraded", "unhealthy")
    assert statuses.get("metrics") in ("degraded", "healthy")
