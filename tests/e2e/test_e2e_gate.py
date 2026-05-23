"""E2E coverage gate: 81 features, 83 scenarios, mode/feedback/policy/LLM summary."""

from __future__ import annotations

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.e2e.preflight import run_preflight
from watchtower.e2e.replay import (
    FEATURE_IDS,
    SCENARIO_IDS,
    ingest_feature_replay,
    ingest_scenario_replay,
)
from watchtower.e2e.report import write_e2e_summary
from watchtower.normalization.service import NormalizationService

TENANT = "e2e-gate-tenant"


def test_e2e_coverage_gate_summary():
    preflight = run_preflight()
    assert preflight.ok

    normalizer = NormalizationService()
    extractor = CandidateExtractor()

    feature_failures: list[str] = []
    for fid in FEATURE_IDS:
        r = ingest_feature_replay(
            normalizer, extractor, tenant_id=TENANT, feature_id=fid
        )
        if r.normalized_count < 1:
            feature_failures.append(fid)

    scenario_failures: list[str] = []
    for sid in SCENARIO_IDS:
        r = ingest_scenario_replay(
            normalizer, extractor, tenant_id=TENANT, scenario_id=sid
        )
        if r.normalized_count < 1:
            scenario_failures.append(sid)

    assert len(feature_failures) == 0, feature_failures[:5]
    assert len(scenario_failures) == 0, scenario_failures[:5]

    summary = {
        "preflight_ok": preflight.ok,
        "features_total": len(FEATURE_IDS),
        "features_ingested_normalized": len(FEATURE_IDS) - len(feature_failures),
        "scenarios_total": len(SCENARIO_IDS),
        "scenarios_ingested_normalized": len(SCENARIO_IDS) - len(scenario_failures),
        "feature_failures": feature_failures,
        "scenario_failures": scenario_failures,
        "real_gate_pass": preflight.real_gate_pass,
        "gates": {
            "81_features": len(feature_failures) == 0,
            "83_scenarios": len(scenario_failures) == 0,
        },
    }
    path = write_e2e_summary(summary)
    assert path.is_file()
    assert summary["gates"]["81_features"]
    assert summary["gates"]["83_scenarios"]
