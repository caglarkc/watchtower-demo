"""LLM explanation does not change deterministic severity."""

from __future__ import annotations

import os

import pytest

from tests.alerts.helpers import produce_real_alert_via_graph
from tests.llm.conftest import valid_alert_explanation_json
from watchtower.llm.gateway import LLMGateway
from watchtower.llm.providers.mock import mock_openai


def test_explanation_preserves_severity_with_mock(app, tenant_id):
    alert_id, _case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        gateway = LLMGateway(
            [mock_openai([valid_alert_explanation_json()])],
            audit_repo=None,
        )
        session.alerts._llm = gateway
        detail = session.alerts.get_alert_detail(tenant_id, alert_id)
        assert detail is not None
        severity_before = detail.alert.severity
        explanation = session.alerts.generate_explanation(tenant_id, alert_id)
        after = session.alerts.get_alert(tenant_id, alert_id)
    assert explanation.get("severity_unchanged") == severity_before
    assert after is not None
    assert after.severity == severity_before


def test_live_gemini_explanation_schema_when_configured(app, tenant_id):
    if os.environ.get("WATCHTOWER_LLM_TEST_PROVIDER") != "gemini":
        pytest.skip("live Gemini not configured")
    if not os.environ.get("WATCHTOWER_GEMINI_API_KEY"):
        pytest.skip("WATCHTOWER_GEMINI_API_KEY not set")

    alert_id, _case_id, _state = produce_real_alert_via_graph(app, tenant_id)
    with app.session() as session:
        detail_before = session.alerts.get_alert_detail(tenant_id, alert_id)
        severity_before = detail_before.alert.severity if detail_before else None
        explanation = session.alerts.generate_explanation(tenant_id, alert_id)
        after = session.alerts.get_alert(tenant_id, alert_id)
    if explanation.get("fail_open"):
        pytest.skip(f"Gemini unavailable: {explanation.get('note')}")
    assert explanation.get("data") is not None
    assert after is not None
    assert after.severity == severity_before
