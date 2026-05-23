"""E2E fixtures: server-stack lab + Watchtower app."""

from __future__ import annotations

import json

import pytest

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.graph.runner import build_graph_runner
from watchtower.llm.gateway import LLMGateway
from watchtower.normalization.service import NormalizationService
from watchtower.services.app import AppContext
from watchtower.e2e.preflight import run_preflight


@pytest.fixture(scope="session")
def server_stack_preflight():
    result = run_preflight()
    result.raise_if_failed()
    return result


@pytest.fixture
def normalizer() -> NormalizationService:
    return NormalizationService()


@pytest.fixture
def extractor() -> CandidateExtractor:
    return CandidateExtractor()


def attach_mock_llm(session, mock_gateway: LLMGateway) -> None:
    session.graph_runner = build_graph_runner(
        mode_controller=session.mode_controller,
        decision=session.decision,
        baseline=session.baseline,
        feedback=session.feedback,
        rules=session.rules,
        graph_repo=session.graph,
        conn=session.conn,
        llm_gateway=mock_gateway,
        alerts=session.alerts,
    )
    session.llm = mock_gateway


@pytest.fixture
def mock_llm_gateway():
    from tests.llm.conftest import valid_alert_explanation_json
    from watchtower.llm.providers.mock import mock_openai

    return LLMGateway(
        [mock_openai([valid_alert_explanation_json()])],
        audit_repo=None,
        max_retries=2,
    )


@pytest.fixture
def app_mock_llm(app: AppContext, mock_llm_gateway: LLMGateway):
    with app.session() as session:
        attach_mock_llm(session, mock_llm_gateway)
        session.conn.commit()
    return app


def seed_baseline_for_candidate(app: AppContext, tenant_id: str, candidate) -> None:
    from tests.graph.conftest import seed_anomaly_baseline

    dept = candidate.attributes.get("department_id")
    seed_anomaly_baseline(
        app,
        tenant_id,
        user_id=str(candidate.attributes.get("user_id") or candidate.actor),
        department_id=str(dept) if dept else "unknown",
        metric_name=str(candidate.attributes.get("metric_name", "event_volume")),
    )
