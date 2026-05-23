"""Mock LLM providers for tests and local development."""

from __future__ import annotations

from typing import Any

from watchtower.llm.capabilities import (
    ANTHROPIC_CAPABILITIES,
    CUSTOM_OPENAI_COMPAT_CAPABILITIES,
    GEMINI_CAPABILITIES,
    OLLAMA_CAPABILITIES,
    OPENAI_CAPABILITIES,
    ProviderCapabilities,
)
from watchtower.llm.protocol import (
    ProviderResponse,
    ProviderUnavailableError,
)


class MockLLMProvider:
    """Configurable mock provider returning scripted responses."""

    def __init__(
        self,
        name: str,
        capabilities: ProviderCapabilities,
        responses: list[str],
        *,
        model: str = "mock-model",
        unavailable: bool = False,
    ) -> None:
        self._name = name
        self._capabilities = capabilities
        self._responses = responses
        self._model = model
        self._unavailable = unavailable
        self._call_count = 0
        self.call_history: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    @property
    def call_count(self) -> int:
        return self._call_count

    def complete_structured(
        self,
        *,
        task: str,
        prompt: str,
        json_schema: dict[str, Any],
        max_tokens: int = 2048,
    ) -> ProviderResponse:
        if self._unavailable:
            raise ProviderUnavailableError(f"{self._name} unavailable")
        self.call_history.append(
            {"task": task, "prompt": prompt, "schema": json_schema, "max_tokens": max_tokens}
        )
        idx = min(self._call_count, len(self._responses) - 1) if self._responses else 0
        self._call_count += 1
        if not self._responses:
            raise ProviderUnavailableError(f"{self._name} has no scripted responses")
        return ProviderResponse(
            raw_text=self._responses[idx],
            provider=self._name,
            model=self._model,
            usage={"prompt_tokens": len(prompt) // 4, "completion_tokens": 50},
        )


def mock_openai(responses: list[str], **kwargs: Any) -> MockLLMProvider:
    return MockLLMProvider("openai", OPENAI_CAPABILITIES, responses, model="gpt-4o-mock", **kwargs)


def mock_anthropic(responses: list[str], **kwargs: Any) -> MockLLMProvider:
    return MockLLMProvider(
        "anthropic", ANTHROPIC_CAPABILITIES, responses, model="claude-mock", **kwargs
    )


def mock_gemini(responses: list[str], **kwargs: Any) -> MockLLMProvider:
    return MockLLMProvider("gemini", GEMINI_CAPABILITIES, responses, model="gemini-mock", **kwargs)


def mock_ollama(responses: list[str], **kwargs: Any) -> MockLLMProvider:
    return MockLLMProvider("ollama", OLLAMA_CAPABILITIES, responses, model="llama-mock", **kwargs)


def mock_custom_openai_compatible(responses: list[str], **kwargs: Any) -> MockLLMProvider:
    return MockLLMProvider(
        "custom_openai_compatible",
        CUSTOM_OPENAI_COMPAT_CAPABILITIES,
        responses,
        model="custom-mock",
        **kwargs,
    )
