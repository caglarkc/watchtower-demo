"""LLM mock replay and unavailable fail-open E2E."""

from __future__ import annotations

from tests.e2e.conftest import attach_mock_llm
from tests.graph.conftest import seed_anomaly_baseline, set_tenant_mode
from tests.llm.conftest import valid_alert_explanation_json
from watchtower.e2e.replay import first_candidate_from_feature
from watchtower.e2e.runner import run_graph_to_completion
from watchtower.llm.gateway import FAIL_OPEN_NOTE
from watchtower.llm.providers.mock import mock_openai


def test_llm_mock_replay_produces_explanation(mock_llm_gateway):
    result = mock_llm_gateway.invoke("alert_explanation", "Explain replay alert.")
    assert result.success is True
    assert result.data is not None
    assert result.data.summary  # type: ignore[attr-defined]


def test_llm_unavailable_path_passes():
    from watchtower.llm.gateway import LLMGateway

    gw = LLMGateway([mock_openai([], unavailable=True)], audit_repo=None, max_retries=2)
    result = gw.invoke("alert_explanation", "no provider")
    assert result.fail_open is True
    assert result.note == FAIL_OPEN_NOTE


def test_graph_llm_mock_explanation_from_replay(
    app_mock_llm, tenant_id, normalizer, extractor, mock_llm_gateway
):
    seed_anomaly_baseline(app_mock_llm, tenant_id)
    set_tenant_mode(app_mock_llm, tenant_id, "hybrid")
    candidate = first_candidate_from_feature(
        normalizer,
        extractor,
        tenant_id=tenant_id,
        feature_id="F-001",
        prefer_anomaly=True,
    )
    assert candidate is not None
    candidate.attributes["volume"] = 500.0

    with app_mock_llm.session() as session:
        attach_mock_llm(session, mock_llm_gateway)
        session.conn.commit()

    result = run_graph_to_completion(app_mock_llm, candidate)
    expl = result.state.get("llm_explanation") or {}
    assert expl.get("skipped") is False
    assert expl.get("fail_open") is not True
    assert expl.get("data") is not None


def test_graph_llm_unavailable_fail_open_passes(app, tenant_id, normalizer, extractor):
    from watchtower.llm.gateway import LLMGateway
    from watchtower.llm.providers.mock import mock_openai

    from tests.e2e.conftest import attach_mock_llm, seed_baseline_for_candidate

    unavailable_gw = LLMGateway(
        [mock_openai([], unavailable=True)],
        audit_repo=None,
        max_retries=2,
    )
    candidate = first_candidate_from_feature(
        normalizer,
        extractor,
        tenant_id=tenant_id,
        feature_id="F-001",
        prefer_anomaly=True,
    )
    assert candidate is not None
    _seed_for_candidate(app, tenant_id, candidate)
    set_tenant_mode(app, tenant_id, "hybrid")
    candidate.attributes["volume"] = 500.0
    with app.session() as session:
        attach_mock_llm(session, unavailable_gw)
        session.conn.commit()
    result = run_graph_to_completion(app, candidate)
    expl = result.state.get("llm_explanation") or {}
    assert expl.get("fail_open") is True
