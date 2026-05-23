"""Learn / run / hybrid mode E2E using server-stack F-001 replay."""

from __future__ import annotations

from tests.graph.conftest import seed_anomaly_baseline, set_tenant_mode
from watchtower.e2e.replay import first_candidate_from_feature
from watchtower.e2e.runner import run_graph_to_completion
from watchtower.candidates.extractor import CandidateExtractor
from watchtower.normalization.service import NormalizationService


def _candidate_from_f001(
    tenant_id: str,
    normalizer: NormalizationService,
    extractor: CandidateExtractor,
):
    cand = first_candidate_from_feature(
        normalizer,
        extractor,
        tenant_id=tenant_id,
        feature_id="F-001",
        prefer_anomaly=True,
    )
    assert cand is not None, "F-001 replay must yield a candidate"
    return cand


def test_learn_mode_zero_alert_silent_and_learning_queue(
    app, tenant_id, normalizer, extractor, server_stack_preflight
):
    del server_stack_preflight
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "learn")
    candidate = _candidate_from_f001(tenant_id, normalizer, extractor)

    result = run_graph_to_completion(app, candidate)
    with app.session() as session:
        alerts = session.graph.count_alerts(tenant_id, result.run_id)
        silent = session.graph.count_silent_findings(tenant_id, result.run_id)
        learning = session.graph.count_learning_events(tenant_id, result.run_id)

    assert alerts == 0
    assert silent >= 1
    assert learning >= 1
    assert result.state.get("learning_event_id")
    assert result.state.get("route", {}).get("should_create_alert") is False


def test_run_mode_expected_alert_no_learning(app, tenant_id, normalizer, extractor):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "run")
    candidate = _candidate_from_f001(tenant_id, normalizer, extractor)
    candidate.attributes["volume"] = 500.0

    with app.session() as session:
        obs_before = session.conn.execute(
            "SELECT COUNT(*) FROM behavior_observations WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        result = run_graph_to_completion(app, candidate)
        obs_after = session.conn.execute(
            "SELECT COUNT(*) FROM behavior_observations WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()[0]
        learning = session.graph.count_learning_events(tenant_id, result.run_id)
        alerts = session.graph.count_alerts(tenant_id, result.run_id)

    assert learning == 0
    assert obs_after == obs_before
    assert alerts >= 1 or result.state.get("alert_id")
    assert result.state.get("route", {}).get("baseline_update_allowed") is False


def test_hybrid_mode_alert_and_controlled_learning(
    app, tenant_id, normalizer, extractor
):
    seed_anomaly_baseline(app, tenant_id)
    set_tenant_mode(app, tenant_id, "hybrid")
    candidate = _candidate_from_f001(tenant_id, normalizer, extractor)
    candidate.attributes["volume"] = 500.0

    result = run_graph_to_completion(app, candidate)
    with app.session() as session:
        alerts = session.graph.count_alerts(tenant_id, result.run_id)
        learning = session.graph.count_learning_events(tenant_id, result.run_id)

    assert alerts >= 1
    assert learning >= 1
    assert result.state.get("route", {}).get("should_enqueue_learning") is True
