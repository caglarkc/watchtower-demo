"""E2E fixtures: server-stack lab + Watchtower app."""

from __future__ import annotations

import json

import pytest

from watchtower.candidates.extractor import CandidateExtractor
from watchtower.e2e.runner import _attach_llm_gateway
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


def attach_mock_llm(session, mock_gateway: LLMGateway, *, checkpoint_store) -> None:
    _attach_llm_gateway(session, mock_gateway, checkpoint_store=checkpoint_store)


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
        attach_mock_llm(session, mock_llm_gateway, checkpoint_store=app.checkpoint_store)
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


def seed_baseline_for_candidate_from_soak(app: AppContext, tenant_id: str, candidate) -> None:
    """Backward-compatible alias used by graph tests."""
    seed_baseline_for_candidate(app, tenant_id, candidate)
