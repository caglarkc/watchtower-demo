"""Google Gemini adapter."""

from __future__ import annotations

import json
from typing import Any

from watchtower.llm.capabilities import GEMINI_CAPABILITIES, ProviderCapabilities
from watchtower.llm.protocol import ProviderResponse, ProviderUnavailableError
from watchtower.llm.providers.base import post_json


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = "gemini-2.0-flash",
    ) -> None:
        self._api_key = api_key
        self._model = model

    @property
    def capabilities(self) -> ProviderCapabilities:
        return GEMINI_CAPABILITIES

    def complete_structured(
        self,
        *,
        task: str,
        prompt: str,
        json_schema: dict[str, Any],
        max_tokens: int = 2048,
    ) -> ProviderResponse:
        if not self._api_key:
            raise ProviderUnavailableError("Gemini API key not configured")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "responseMimeType": "application/json",
                "responseSchema": json_schema,
            },
        }
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._api_key}"
        )
        data = post_json(url, payload, {})
        candidates = data.get("candidates", [])
        text = "{}"
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                text = parts[0].get("text", "{}")
        return ProviderResponse(
            raw_text=text,
            provider=self.name,
            model=self._model,
            usage=data.get("usageMetadata", {}),
        )
