"""Provider capability registry."""

from __future__ import annotations

from pydantic import BaseModel, Field

ProviderName = str


class ProviderCapabilities(BaseModel):
    structured_output: bool = False
    tool_calling: bool = False
    json_schema_strict: bool = False
    streaming: bool = False
    local: bool = False
    max_context_tokens: int = Field(default=8192, ge=1)
    supports_responses_api: bool = False
    supports_chat_completions: bool = True


OPENAI_CAPABILITIES = ProviderCapabilities(
    structured_output=True,
    tool_calling=True,
    json_schema_strict=True,
    streaming=True,
    local=False,
    max_context_tokens=128_000,
    supports_responses_api=True,
    supports_chat_completions=True,
)

ANTHROPIC_CAPABILITIES = ProviderCapabilities(
    structured_output=True,
    tool_calling=True,
    json_schema_strict=False,
    streaming=True,
    local=False,
    max_context_tokens=200_000,
    supports_responses_api=False,
    supports_chat_completions=True,
)

GEMINI_CAPABILITIES = ProviderCapabilities(
    structured_output=True,
    tool_calling=True,
    json_schema_strict=True,
    streaming=True,
    local=False,
    max_context_tokens=1_000_000,
    supports_responses_api=False,
    supports_chat_completions=True,
)

OLLAMA_CAPABILITIES = ProviderCapabilities(
    structured_output=True,
    tool_calling=False,
    json_schema_strict=False,
    streaming=True,
    local=True,
    max_context_tokens=32_768,
    supports_responses_api=False,
    supports_chat_completions=True,
)

CUSTOM_OPENAI_COMPAT_CAPABILITIES = ProviderCapabilities(
    structured_output=True,
    tool_calling=False,
    json_schema_strict=False,
    streaming=True,
    local=True,
    max_context_tokens=32_768,
    supports_responses_api=False,
    supports_chat_completions=True,
)

CAPABILITY_REGISTRY: dict[ProviderName, ProviderCapabilities] = {
    "openai": OPENAI_CAPABILITIES,
    "anthropic": ANTHROPIC_CAPABILITIES,
    "gemini": GEMINI_CAPABILITIES,
    "ollama": OLLAMA_CAPABILITIES,
    "custom_openai_compatible": CUSTOM_OPENAI_COMPAT_CAPABILITIES,
}


def get_capabilities(provider: ProviderName) -> ProviderCapabilities:
    if provider not in CAPABILITY_REGISTRY:
        msg = f"Unknown provider: {provider}"
        raise KeyError(msg)
    return CAPABILITY_REGISTRY[provider]
