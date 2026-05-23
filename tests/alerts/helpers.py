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
    result = run_graph_to_completion(app, candidate)
    alert_id = result.state.get("alert_id")
    case_id = result.state.get("alert_case_id")
    assert alert_id, "graph must produce alert in run mode"
    assert case_id, "graph must produce case in run mode"
    return alert_id, case_id, result.state
