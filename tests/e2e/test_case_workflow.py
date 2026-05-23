"""E2E case workflow on daemon/graph-produced real alerts."""

from __future__ import annotations

from tests.alerts.helpers import produce_real_alert_via_graph
from tests.daemon.helpers import db_pipeline_counts, register_f001_jsonl_source, replay_events_to_jsonl
from tests.graph.conftest import set_tenant_mode
from watchtower.daemon.service import DaemonService


def test_daemon_run_mode_produces_alert_case(app, tenant_id, tmp_path):
    jsonl = replay_events_to_jsonl("F-001", tmp_path / "f001_case.jsonl")
    register_f001_jsonl_source(app, tenant_id, jsonl)
    from tests.alerts.helpers import produce_real_alert_via_graph as _  # noqa: F401

    from tests.e2e.conftest import seed_baseline_for_candidate
    from watchtower.candidates.extractor import CandidateExtractor
    from watchtower.e2e.replay import first_candidate_from_feature
    from watchtower.normalization.service import NormalizationService

    set_tenant_mode(app, tenant_id, "run")
    normalizer = NormalizationService()
    extractor = CandidateExtractor()
    candidate = first_candidate_from_feature(
        normalizer, extractor, tenant_id=tenant_id, feature_id="F-001"
    )
    assert candidate
    candidate.attributes["volume"] = 500.0
    seed_baseline_for_candidate(app, tenant_id, candidate)

    with app.session() as session:
        DaemonService(session).run_once(tenant_id)
        session.conn.commit()

    counts = db_pipeline_counts(app, tenant_id)
    assert counts["alerts"] >= 1
    assert counts["graph_runs"] >= 1

    with app.session() as session:
        alerts = session.alerts.list_alerts(tenant_id, limit=5)
        assert alerts
        case = session.alerts._repo.get_case_by_alert(tenant_id, alerts[0].id)
        assert case is not None
        timeline = session.alerts.get_timeline(tenant_id, case_id=case.id)
    assert any(t.event_type == "created" for t in timeline)


def test_query_cites_store_backed_cases(app, tenant_id):
    produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        result = session.query.answer(
            tenant_id, "show recent alerts and case timeline"
        )
    assert result["auditable"] is True
    assert any(s["type"] == "cases" for s in result["sources"])
    assert "case:" in result["answer"] or "Cases stored" in result["answer"]
