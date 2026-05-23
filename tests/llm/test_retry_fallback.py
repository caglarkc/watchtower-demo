"""Retry and provider fallback."""

from __future__ import annotations

import json

import pytest

from watchtower.llm.providers.mock import mock_anthropic, mock_openai
from tests.llm.conftest import valid_alert_explanation_json


def test_invalid_json_retry_works(gateway_with_audit):
    valid = valid_alert_explanation_json()
    provider = mock_openai([ "not-json", "{still bad", valid])
    gw = gateway_with_audit([provider])
    result = gw.invoke("alert_explanation", "retry test")
    assert result.success is True
    assert provider.call_count == 3


def test_schema_outside_output_rejected(gateway_with_audit):
    bad = json.dumps({"summary": "x"})  # missing required list fields? summary ok but risk_factors has default
    wrong = json.dumps({"totally": "wrong"})
    provider = mock_openai([wrong, wrong, valid_alert_explanation_json()])
    gw = gateway_with_audit([provider])
    result = gw.invoke("alert_explanation", "schema test")
    assert result.success
    assert provider.call_count >= 2


def test_provider_fallback_works(gateway_with_audit):
    primary = mock_openai([valid_alert_explanation_json()], unavailable=True)
    secondary = mock_anthropic([valid_alert_explanation_json()])
    gw = gateway_with_audit([primary, secondary])
    result = gw.invoke("alert_explanation", "fallback")
    assert result.success
    assert result.provider == "anthropic"
    assert primary.call_count == 0


def test_forbidden_decision_task_rejected(gateway_with_audit):
    gw = gateway_with_audit([mock_openai([valid_alert_explanation_json()])])
    with pytest.raises(ValueError, match="forbidden"):
        gw.invoke("alert_decision", "decide severity")
