"""LLM test fixtures."""

from __future__ import annotations

import json

import pytest

from watchtower.llm.gateway import LLMGateway
from watchtower.services.app import AppContext
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
def gateway_with_audit(app: AppContext):
    def _build(providers):
        return LLMGateway(providers, audit_repo=None, max_retries=2)

    return _build


@pytest.fixture
def gateway_with_db_audit(app: AppContext):
    class _AuditProxy:
        def insert(self, **kwargs):
            with app.session() as session:
                return LLMCallAuditRepository(session.conn).insert(**kwargs)

    def _build(providers):
        return LLMGateway(providers, audit_repo=_AuditProxy(), max_retries=2)

    return _build
