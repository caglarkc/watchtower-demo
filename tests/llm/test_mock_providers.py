"""Mock provider adapter tests."""

from __future__ import annotations

from watchtower.llm.providers.mock import (
    mock_anthropic,
    mock_custom_openai_compatible,
    mock_gemini,
    mock_ollama,
    mock_openai,
)
from tests.llm.conftest import valid_alert_explanation_json


def test_mock_openai_provider_pass(gateway_with_audit):
    gw = gateway_with_audit([mock_openai([valid_alert_explanation_json()])])
    result = gw.invoke("alert_explanation", "Explain this alert.")
    assert result.success is True
    assert result.provider == "openai"
    assert result.data is not None
    assert result.data.summary  # type: ignore[attr-defined]


def test_mock_anthropic_provider_pass(gateway_with_audit):
    gw = gateway_with_audit([mock_anthropic([valid_alert_explanation_json()])])
    result = gw.invoke("alert_explanation", "Explain.")
    assert result.success
    assert result.provider == "anthropic"


def test_mock_gemini_provider_pass(gateway_with_audit):
    gw = gateway_with_audit([mock_gemini([valid_alert_explanation_json()])])
    result = gw.invoke("alert_explanation", "Explain.")
    assert result.success
    assert result.provider == "gemini"


def test_mock_ollama_compatible_provider_pass(gateway_with_audit):
    gw = gateway_with_audit([mock_ollama([valid_alert_explanation_json()])])
    result = gw.invoke("alert_explanation", "Explain.")
    assert result.success
    assert result.provider == "ollama"

    gw2 = gateway_with_audit(
        [mock_custom_openai_compatible([valid_alert_explanation_json()])]
    )
    result2 = gw2.invoke("alert_explanation", "Explain.")
    assert result2.success
    assert result2.provider == "custom_openai_compatible"
