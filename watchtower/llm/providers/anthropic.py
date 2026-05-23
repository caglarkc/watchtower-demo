"""Anthropic adapter."""

from __future__ import annotations

import json
from typing import Any

from watchtower.llm.capabilities import ANTHROPIC_CAPABILITIES, ProviderCapabilities
from watchtower.llm.protocol import ProviderResponse, ProviderUnavailableError
from watchtower.llm.providers.base import post_json


class AnthropicProvider:
    name = "anthropic"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "claude-3-5-sonnet-20241022",
    ) -> None:
        self._api_key = api_key
        self._model = model

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ANTHROPIC_CAPABILITIES

    def complete_structured(
        self,
        *,
        task: str,
        prompt: str,
        json_schema: dict[str, Any],
        max_tokens: int = 2048,
    ) -> ProviderResponse:
        if not self._api_key:
            raise ProviderUnavailableError("Anthropic API key not configured")
        payload = {
            "model": self._model,
            "max_tokens": max_tokens,
            "system": f"Return JSON matching schema for task {task}.",
            "messages": [{"role": "user", "content": prompt}],
        }
        data = post_json(
            "https://api.anthropic.com/v1/messages",
            payload,
            {
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        parts = data.get("content", [])
        text = parts[0]["text"] if parts else "{}"
        return ProviderResponse(
            raw_text=text,
            provider=self.name,
            model=self._model,
            usage=data.get("usage", {}),
        )
