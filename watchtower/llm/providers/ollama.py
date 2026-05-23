"""Ollama OpenAI-compatible adapter."""

from __future__ import annotations

from typing import Any

from watchtower.llm.capabilities import OLLAMA_CAPABILITIES, ProviderCapabilities
from watchtower.llm.providers.openai_compatible import OpenAICompatibleProvider


class OllamaProvider(OpenAICompatibleProvider):
    """Ollama local server (OpenAI-compatible /v1/chat/completions)."""

    name = "ollama"

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434/v1",
        model: str = "llama3.2",
        api_key: str | None = "ollama",
    ) -> None:
        super().__init__(
            name="ollama",
            capabilities=OLLAMA_CAPABILITIES,
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
