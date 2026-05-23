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
- Live Gemini contract/integration testi, `.env` icindeki test provider bilgileri varsa calistirilabilir.
- Invalid JSON retry.
- Provider fallback.
- LLM unavailable fail-open.
- Schema dışı output kullanılmaz.

# Live Gemini Test Konfigürasyonu

LLM testleri mock provider'a bagimli kalmalidir; live provider testi mock testlerin yerine gecmez, sadece ek kanit olarak calisir.

`.env` icinde su degiskenler varsa live Gemini testleri bunlari kullanir:

- `WATCHTOWER_LLM_TEST_PROVIDER=gemini`
- `WATCHTOWER_GEMINI_API_KEY`
- `WATCHTOWER_GEMINI_MODEL=gemini-3.1-flash-lite`

Kurallar:

- API key asla repoya commit edilmez; `.env` ignored kalmalidir.
- Live Gemini testi yoksa veya provider unavailable ise mock provider testleri yine pass olmalidir.
- Live Gemini testleri LLM'in final alert karari verdigini degil, provider adapter, structured output ve fallback davranisini dogrular.
- Lokal AI/Ollama zorunlu degildir; Gemini test provider olarak yeterlidir.

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
