"""Ollama-compatible local endpoint contract (mock + adapter shape)."""

from __future__ import annotations

import inspect

from watchtower.llm.capabilities import OLLAMA_CAPABILITIES
from watchtower.llm.providers.mock import mock_ollama
from watchtower.llm.providers.ollama import OllamaProvider
from tests.llm.conftest import valid_alert_explanation_json


def test_ollama_provider_openai_compatible_contract():
    provider = OllamaProvider(base_url="http://127.0.0.1:11434/v1", model="llama3.2")
    assert provider.name == "ollama"
    assert "/v1" in provider._base_url  # noqa: SLF001
    assert OLLAMA_CAPABILITIES.local is True
    assert OLLAMA_CAPABILITIES.supports_chat_completions is True
    sig = inspect.signature(provider.complete_structured)
    assert "prompt" in sig.parameters


def test_ollama_mock_replay_contract_passes():
    from watchtower.llm.gateway import LLMGateway

    gw = LLMGateway([mock_ollama([valid_alert_explanation_json()])], audit_repo=None)
    result = gw.invoke("alert_explanation", "Contract replay")
    assert result.success
    assert result.provider == "ollama"
