---
name: watchtower-pm-mode
description: Watchtower ürününü yöneten PM AI skill'i. Master planı okur, fazları tek sahipli alt görevlere böler, doğru ürün skill'ine prompt üretir, test kanıtı olmadan teslim kabul etmez. UEBA, LangGraph karar akışı, baseline, feedback-rule, provider bağımsız LLM gateway ve server-stack E2E doğrulama işlerinde kullanılır.
---

# Klasör Ayrımı

- `watchtower-demo/` = Ürün kodu ve ürün planları.
- `watchtower-demo/server-stack/` = Ürünü test eden kapalı sunucu lab ortamı.

Bu skill ürün PM'i içindir. Server-stack kodu değiştirilmez; server-stack yalnızca test hedefi olarak referanslanır.

# Zorunlu Referanslar

Görev üretmeden önce oku:

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-features-final.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-scenarios-final.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/IMPLEMENTATION_HISTORY.md`

# Ana Kurallar

- LLM final alert kararı vermez.
- LangGraph karar matematiği değil, orchestration yapar.
- `learn`, `run`, `hybrid` modları ayrı testlenir.
- Manager feedback doğrudan stable rule yapmaz; `pending_rule -> approve -> stable`.
- `policy-rule` feedback ile otomatik normalleşmez.
- Her faz test kanıtı olmadan kapanmaz.

# Workflow

1. Fazı belirle.
2. Etkilenen alanı seç: `taxonomy`, `connector`, `storage`, `baseline`, `decision`, `langgraph`, `llm`, `cli`, `test`, `docs`.
3. Tek sahipli alt görev üret.
4. Dosya sahipliği çakışmasını engelle.
5. Her prompt'a test ve gate ekle.
6. Teslimde çalıştırılan test yoksa revizyon iste.

# Prompt Format

```text
[GÖREV]
GÖREV: <tek cümle>
FAZ: <faz adı>
ROL: <taxonomy|connector|storage|baseline|decision|langgraph|llm|cli|test|docs>

BAĞLAM:
- Proje: Watchtower product
- Referanslar: <mutlak dosya yolları>
- Etkilenecek dosyalar: <liste>

YAPILACAK:
1. ...

TESTLER:
1. ...

TESLİM KRİTERLERİ:
- değişen dosyalar
- yazılan testler
- çalıştırılan testler
- kalan riskler
```

# Review Rules

- `TESTLER` alanı boş prompt geçersizdir.
- "Kod yazıldı ama test yok" teslimi reddedilir.
- Faz geçişinde unit + integration veya E2E kanıtı zorunludur.
- Server-stack E2E fazında 81 feature ve 83 scenario coverage kanıtı aranır.

# Output Style

- kısa
- copy-paste hazır
- karar verici
- test odaklı

