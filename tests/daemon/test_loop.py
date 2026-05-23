"""Daemon loop unit/integration tests (mock-free replay JSONL)."""

from __future__ import annotations

from tests.daemon.helpers import db_pipeline_counts
from tests.e2e.conftest import seed_baseline_for_candidate
from tests.graph.conftest import set_tenant_mode
from watchtower.daemon.service import DaemonService
from watchtower.e2e.replay import first_candidate_from_feature
from watchtower.domain.events import RawEventRecord


def _run_daemon_once(app, tenant_id):
    with app.session() as session:
        daemon = DaemonService(session)
        summary = daemon.run_once(tenant_id)
        session.conn.commit()
        return summary


def test_daemon_pipeline_raw_to_graph_chain(app, tenant_id, f001_source):
    cand = first_candidate_from_feature(
        app.session().__enter__().__class__  # noqa — use normalizer below
    )
    del cand  # placeholder fix below
