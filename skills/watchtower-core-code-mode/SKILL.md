---
name: watchtower-core-code-mode
description: Watchtower ürün core kodunu yazan AI skill'i. Storage, connector, normalization, baseline, feedback, policy, severity, CLI ve domain modellerini master plana uygun uygular. Her değişiklikte test veya doğrulama kanıtı üretir.
---

# Kapsam

Bu skill `watchtower-demo/` ürün kodunda çalışır.

Kapsam dahilinde:

- `watchtower/` Python package
- storage ve migrations
- connector abstraction
- unified event schema
- baseline engine
- feedback-rule engine
- policy/severity engine
- CLI

Kapsam dışında:

- `server-stack/` servislerini değiştirmek
- LLM'e final alert kararı verdirmek
- auto-remediation

# Zorunlu Referanslar

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md`

# Kod Kuralları

- Async I/O tercih edilir.
- Type hint zorunlu.
- Pydantic/dataclass schema net olmalı.
- Her engine bağımsız unit testlenebilir olmalı.
- LangGraph node içine karar matematiği gömülmez.
- LLM provider çağrıları core decision path'i bloklamaz.
- Multi-tenant veri izolasyonu bozulmaz.

# Watchtower Karar Kuralları

- `policy-rule` ve `hard-rule` baseline beklemez.
- `baseline-anomaly` kullanıcı/departman/rol profiliyle değerlendirilir.
- `cross-signal` en az iki kaynak sinyal ister.
- Manager feedback `pending_rule` üretir; stable rule için approval gerekir.
- `learn` modunda alert yok, `silent_candidate_finding` var.
- `run` modunda öğrenme update'i yok.
- `hybrid` modunda kontrollü öğrenme var.

# Teslim Formatı

```text
YAPILAN İŞ:
- ...

DEĞİŞEN DOSYALAR:
- path — değişiklik

AKTİF DAVRANIŞLAR:
- ...

YAZILAN TESTLER:
- ...

ÇALIŞTIRILAN TESTLER:
- ...

KALAN RİSKLER:
- ...
```

