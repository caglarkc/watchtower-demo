"""Custom OpenAI-compatible endpoint adapter."""

from __future__ import annotations

import json
from typing import Any

from watchtower.llm.capabilities import (
    CUSTOM_OPENAI_COMPAT_CAPABILITIES,
    ProviderCapabilities,
)
from watchtower.llm.protocol import ProviderResponse, ProviderUnavailableError
from watchtower.llm.providers.base import post_json


class OpenAICompatibleProvider:
    """OpenAI-compatible chat completions API (Ollama, vLLM, etc.)."""

    def __init__(
        self,
        *,
        name: str = "custom_openai_compatible",
        capabilities: ProviderCapabilities | None = None,
        api_key: str | None = None,
        model: str = "default",
        base_url: str,
    ) -> None:
        self._name = name
        self._capabilities = capabilities or CUSTOM_OPENAI_COMPAT_CAPABILITIES
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    def complete_structured(
        self,
        *,
        task: str,
        prompt: str,
        json_schema: dict[str, Any],
        max_tokens: int = 2048,
    ) -> ProviderResponse:
        if not self._base_url:
            raise ProviderUnavailableError(f"{self._name} base URL not configured")
        headers: dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Task: {task}. Respond with JSON matching schema: "
                        f"{json.dumps(json_schema)[:500]}"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
        }
        data = post_json(
            f"{self._base_url}/chat/completions",
            payload,
            headers,
        )
        text = data["choices"][0]["message"]["content"]
        return ProviderResponse(
            raw_text=text,
            provider=self.name,
            model=self._model,
            usage=data.get("usage", {}),
        )


class CustomOpenAICompatibleProvider(OpenAICompatibleProvider):
    """Named custom OpenAI-compatible provider."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "default",
        base_url: str,
    ) -> None:
        super().__init__(
            name="custom_openai_compatible",
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
