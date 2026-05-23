"""LLM provider protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from watchtower.llm.capabilities import ProviderCapabilities


@dataclass
class ProviderResponse:
    """Raw provider response before schema validation."""

    raw_text: str
    provider: str
    model: str
    usage: dict[str, Any] = field(default_factory=dict)


class ProviderUnavailableError(Exception):
    """Provider cannot serve the request (missing config or outage)."""


class ProviderResponseError(Exception):
    """Provider returned unusable content."""

    def __init__(self, message: str, *, raw_text: str | None = None) -> None:
        super().__init__(message)
        self.raw_text = raw_text


@runtime_checkable
class LLMProvider(Protocol):
    """Provider adapter contract."""

    @property
    def name(self) -> str: ...

    @property
    def capabilities(self) -> ProviderCapabilities: ...

    def complete_structured(
        self,
        *,
        task: str,
        prompt: str,
        json_schema: dict[str, Any],
        max_tokens: int = 2048,
    ) -> ProviderResponse: ...
