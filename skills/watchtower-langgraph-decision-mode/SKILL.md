---
name: watchtower-langgraph-decision-mode
description: Watchtower LangGraph karar orchestration skill'i. Decision graph, checkpoint, node schemas, mode routing, human-in-the-loop approval ve graph audit işlerinde kullanılır. Karar matematiğini graph node'larına gömmeden bağımsız engine'leri orkestre eder.
---

# Amaç

LangGraph, Watchtower'da orchestration katmanıdır.

Yapacağı işler:

- candidate event'i node'lardan geçirmek
- mode'a göre branch almak
- checkpoint/recovery sağlamak
- approval interrupt yönetmek
- graph run audit yazmak
- LLM branch'lerini koşullu çalıştırmak

Yapmayacağı işler:

- threshold matematiği
- baseline hesaplama
- final alert kararı için LLM'e sorma
- feedback'i otomatik stable rule yapma

# Zorunlu Referanslar

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-product-decisions.md`

# Node Sözleşmesi

Node output'ları schema validated olmalıdır.

Zorunlu node'lar:

1. `load_mode`
2. `resolve_identity`
3. `resolve_asset`
4. `load_feature_taxonomy`
5. `load_policy_context`
6. `load_baseline_context`
7. `load_feedback_context`
8. `load_change_context`
9. `score_candidate`
10. `decide_severity`
11. `route_by_mode`
12. `persist_silent_finding`
13. `create_alert_case`
14. `maybe_generate_llm_explanation`
15. `maybe_generate_pending_rule`
16. `await_rule_approval`
17. `finalize_decision`

# Test Kuralları

- Learn mode: 0 alert, silent finding var.
- Run mode: baseline update yok.
- Hybrid mode: alert + controlled learning.
- Crash recovery checkpoint testlenir.
- Pending rule approval sonrası graph devam eder.
- Node output validation fail ettiğinde graph güvenli durur.

# Teslim Formatı

```text
GRAPH DEĞİŞİKLİĞİ:
NODE'LAR:
EDGE/ROUTING:
CHECKPOINT/AUDIT:
TESTLER:
ÇALIŞTIRILAN KOMUTLAR:
RİSKLER:
```

