"""OpenAI adapter."""

from __future__ import annotations

import json
from typing import Any

from watchtower.llm.capabilities import OPENAI_CAPABILITIES, ProviderCapabilities
from watchtower.llm.protocol import ProviderResponse, ProviderUnavailableError
from watchtower.llm.providers.base import post_json


class OpenAIProvider:
    name = "openai"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")

    @property
    def capabilities(self) -> ProviderCapabilities:
        return OPENAI_CAPABILITIES

    def complete_structured(
        self,
        *,
        task: str,
        prompt: str,
        json_schema: dict[str, Any],
        max_tokens: int = 2048,
    ) -> ProviderResponse:
        if not self._api_key:
            raise ProviderUnavailableError("OpenAI API key not configured")
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": "Respond with JSON only matching the provided schema.",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": task, "schema": json_schema, "strict": True},
            },
            "max_tokens": max_tokens,
        }
        data = post_json(
            f"{self._base_url}/chat/completions",
            payload,
            {"Authorization": f"Bearer {self._api_key}"},
        )
        text = data["choices"][0]["message"]["content"]
        return ProviderResponse(
            raw_text=text if isinstance(text, str) else json.dumps(text),
            provider=self.name,
            model=self._model,
            usage=data.get("usage", {}),
        )
