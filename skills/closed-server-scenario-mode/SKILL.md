---
name: closed-server-scenario-mode
description: Watchtower kapalı sunucu simülasyonu için senaryo üretim AI skill'i. 83 senaryo kütüphanesindeki olayları deterministic replay scriptlerine çevirir, user seed ve davranış akışlarını tasarlar, feature coverage ile senaryo coverage arasında eşleme yapar. Kapalı iç ağ senaryoları ve davranış simülasyonu işlerinde kullanılır.
---

# Purpose

Bu skill senaryo ve davranış simülasyonu yazan AI içindir.

Kapsam:

- `simulation/scenarios/`
- deterministic replay
- user seed tasarımı
- behavior DSL veya YAML
- scenario to feature mapping

# Rules

- Her senaryo tekrar çalıştırılabilir olmalı.
- Random varsa seed sabitlenmeli.
- Senaryo gerçek rol bağlamı içermeli.
- Her senaryo için beklenen alert veya beklenen sessizlik açık yazılmalı.
- Senaryo yazıldıysa onun çalıştırma komutu ve test assertion’ı da yazılmalı.

# Zorunlu Eşleme

Her senaryo tesliminde bunlar bulunur:

- `scenario_id`
- hedef feature'lar
- kullanılan servisler
- üretilen log türleri
- beklenen alert seviyesi
- negative control

# Referanslar

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/close-server-simulation-implementation-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-features-final.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-scenarios-final.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-tool-stack.md`

# Teslim

```text
SENARYO:
HEDEF FEATURE'LAR:
KULLANILAN SERVİSLER:
ÜRETİLEN EVENTLER:
TESTLER:
BEKLENEN ALERTLER:
NOTLAR:
```
