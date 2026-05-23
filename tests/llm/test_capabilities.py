"""Capability registry."""

from __future__ import annotations

from watchtower.llm.capabilities import CAPABILITY_REGISTRY, get_capabilities


def test_capability_matrix_fields():
    required = {
        "structured_output",
        "tool_calling",
        "json_schema_strict",
        "streaming",
        "local",
        "max_context_tokens",
        "supports_responses_api",
        "supports_chat_completions",
    }
    for name in ("openai", "anthropic", "gemini", "ollama", "custom_openai_compatible"):
        caps = get_capabilities(name)
        data = caps.model_dump()
        assert required <= set(data.keys())
        assert data["max_context_tokens"] > 0

    assert set(CAPABILITY_REGISTRY.keys()) == {
        "openai",
        "anthropic",
        "gemini",
        "ollama",
        "custom_openai_compatible",
    }
