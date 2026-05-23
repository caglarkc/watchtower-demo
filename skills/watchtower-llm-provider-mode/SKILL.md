---
name: watchtower-llm-provider-mode
description: Watchtower provider bağımsız LLM gateway skill'i. OpenAI, Anthropic, Gemini, Ollama ve custom OpenAI-compatible adapterları, capability registry, structured output validation, retry/fallback ve LLM audit işlerinde kullanılır.
---

# Amaç

LLM gateway, Watchtower'ın provider bağımsız açıklama ve öneri katmanıdır.

Desteklenmesi gereken providerlar:

- OpenAI
- Anthropic
- Gemini
- Ollama
- Custom OpenAI-compatible endpoint

# Kesin Sınırlar

- LLM final alert kararı vermez.
- LLM stable rule yazmaz.
- LLM tool çağırsa bile tool'u uygulama çalıştırır.
- LLM output'u schema validation'dan geçmeden kullanılmaz.
- LLM yoksa sistem fail-open çalışır.

# Capability Registry

Her provider için tutulacak alanlar:

- `structured_output`
- `tool_calling`
- `json_schema_strict`
- `streaming`
- `local`
- `max_context_tokens`
- `supports_responses_api`
- `supports_chat_completions`

# LLM Görevleri

- `AlertExplanation`
- `RuleCandidateDraft`
- `UnknownSchemaMapping`
- `BaselineSummary`
- `MonthlyLearningReport`
- `OperatorQueryAnswer`

# Test Kuralları

- Mock OpenAI provider.
- Mock Anthropic provider.
- Mock Gemini provider.
- Mock Ollama/OpenAI-compatible provider.
- Invalid JSON retry.
- Provider fallback.
- LLM unavailable fail-open.
- Schema dışı output kullanılmaz.

# Teslim Formatı

```text
PROVIDER DEĞİŞİKLİĞİ:
SCHEMA'LAR:
FALLBACK/RETRY:
AUDIT:
TESTLER:
ÇALIŞTIRILAN KOMUTLAR:
RİSKLER:
```

