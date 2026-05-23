---
name: watchtower-test-mode
description: Watchtower ürün test ve QA skill'i. Feature taxonomy, connector, normalization, baseline, feedback, decision engine, LangGraph, LLM gateway, CLI ve server-stack E2E testlerini tasarlar ve çalıştırır.
---

# Amaç

Bu skill Watchtower ürününün test kanıtından sorumludur.

Öncelik sırası:

1. Unit tests
2. Contract tests
3. Decision table tests
4. LangGraph node tests
5. LLM provider mock tests
6. CLI integration tests
7. Server-stack E2E tests
8. Soak/load tests

# Zorunlu Test Yüzeyleri

- 81/81 feature taxonomy
- `policy-rule` suppression guard
- `learn`, `run`, `hybrid` mode routing
- baseline profile math
- feedback pending approval flow
- connector cursor/deduplication
- normalized event schema
- candidate extractor
- severity decision examples
- LLM unavailable fail-open
- provider fallback
- graph checkpoint recovery
- alert lifecycle
- server-stack 81 feature / 83 scenario E2E

# Watchtower Test Kuralları

- Her positive testin negative/control karşılığı olmalı.
- LLM testleri gerçek provider'a bağımlı olmamalı; mock provider zorunlu.
- `.env` icinde Gemini test provider bilgileri varsa live Gemini contract/integration testi ek kanit olarak calistirilir.
- Server-stack E2E testlerinde ürün kodu server-stack içine gömülmez.
- Karar testleri explainable score breakdown assert eder.
- Feedback testleri scope dışı event'in tekrar alert ürettiğini kanıtlar.

# Live LLM Test Kuralları

Live LLM testleri icin `.env` degiskenleri:

- `WATCHTOWER_LLM_TEST_PROVIDER=gemini`
- `WATCHTOWER_GEMINI_API_KEY`
- `WATCHTOWER_GEMINI_MODEL=gemini-3.1-flash-lite`

Kurallar:

- API key commit edilmez; `.env` ignored kalmalidir.
- Live Gemini testi mock provider testlerinin yerine gecmez.
- Live Gemini testi sadece adapter, provider auth, structured output contract ve fallback davranisini dogrular.
- Live provider unavailable ise sistem fail-open davranisini ve mock testleri korumalidir.
- Lokal AI/Ollama zorunlu degildir.

# Teslim Formatı

```text
TEST KAPSAMI:
YAZILAN TESTLER:
ÇALIŞTIRILAN TESTLER:
SONUÇ:
FAIL VARSA:
EKSİK KALAN YÜZEYLER:
RİSKLER:
```
