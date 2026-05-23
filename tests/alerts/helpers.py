"""Helpers to produce real alerts via graph E2E (mock-free)."""

from __future__ import annotations

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.e2e.replay import first_candidate_from_feature
from watchtower.e2e.runner import run_graph_to_completion
from watchtower.normalization.service import NormalizationService
from watchtower.services.app import AppContext
from tests.e2e.conftest import seed_baseline_for_candidate
from tests.graph.conftest import set_tenant_mode


def produce_real_alert_via_graph(
    app: AppContext,
    tenant_id: str,
    *,
    mode: str = "run",
) -> tuple[str, str, dict]:
    """Run graph in run mode; return (alert_id, case_id, graph_state)."""
    set_tenant_mode(app, tenant_id, mode)
    normalizer = NormalizationService()
    extractor = CandidateExtractor()
    candidate = first_candidate_from_feature(
        normalizer,
        extractor,
        tenant_id=tenant_id,
        feature_id="F-001",
        prefer_anomaly=True,
    )
    assert candidate is not None
    candidate.attributes["volume"] = 500.0
    seed_baseline_for_candidate(app, tenant_id, candidate)
    result = run_graph_to_completion(
        app,
        candidate,
        resume_payload={"decision": "approved", "approver_id": "test-operator"},
    )
    case_id = result.state.get("alert_case_id")
    alert_id = result.state.get("alert_id")
    if case_id and not alert_id:
        with app.session() as session:
            case = session.alerts.get_case(tenant_id, case_id)
            if case:
                alert_id = case.alert_id
    if not alert_id:
        with app.session() as session:
            rows = session.alerts.list_alerts(tenant_id, limit=1)
            if rows:
                alert_id = rows[0].id
                case = session.alerts._repo.get_case_by_alert(tenant_id, alert_id)
                case_id = case.id if case else case_id
    assert alert_id, "graph must produce alert in run/hybrid mode"
    assert case_id, "graph must produce case in run/hybrid mode"
    return alert_id, case_id, result.state
