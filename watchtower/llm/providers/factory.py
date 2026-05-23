"""Build provider chain from settings."""

from __future__ import annotations

from watchtower.config.settings import WatchtowerSettings
from watchtower.llm.protocol import LLMProvider
from watchtower.llm.providers.anthropic import AnthropicProvider
from watchtower.llm.providers.gemini import GeminiProvider
from watchtower.llm.providers.ollama import OllamaProvider
from watchtower.llm.providers.openai import OpenAIProvider
from watchtower.llm.providers.openai_compatible import CustomOpenAICompatibleProvider


def build_provider_chain(settings: WatchtowerSettings) -> list[LLMProvider]:
    """Instantiate providers in configured fallback order."""
    names = [n.strip() for n in settings.llm_provider_chain.split(",") if n.strip()]
    providers: list[LLMProvider] = []
    for name in names:
        provider = _provider_for_name(name, settings)
        if provider is not None:
            providers.append(provider)
    return providers


def _provider_for_name(name: str, settings: WatchtowerSettings) -> LLMProvider | None:
    if name == "openai":
        return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    if name == "anthropic":
        return AnthropicProvider(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        )
    if name == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
    if name == "ollama":
        return OllamaProvider(base_url=settings.ollama_base_url, model=settings.ollama_model)
    if name == "custom_openai_compatible":
        if not settings.custom_openai_base_url:
            return None
        return CustomOpenAICompatibleProvider(
            api_key=settings.custom_openai_api_key,
            model=settings.custom_openai_model,
            base_url=settings.custom_openai_base_url,
        )
    return None
