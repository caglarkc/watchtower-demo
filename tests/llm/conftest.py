"""LLM test fixtures."""

from __future__ import annotations

import json

import pytest

from watchtower.llm.gateway import LLMGateway
from watchtower.storage.repositories.llm_audit import LLMCallAuditRepository


def valid_alert_explanation_json() -> str:
    return json.dumps(
        {
            "summary": "Unusual SQL volume outside user baseline.",
            "risk_factors": ["off-hours access", "volume spike"],
            "recommended_actions": ["Review session logs"],
            "confidence_note": "Deterministic severity already set by rule engine.",
        }
    )


@pytest.fixture
def llm_audit_repo(app):
    with app.session() as session:
        yield LLMCallAuditRepository(session.conn)


@pytest.fixture
def gateway_with_audit(llm_audit_repo):
    def _build(providers):
        return LLMGateway(providers, audit_repo=llm_audit_repo, max_retries=2)

    return _build
