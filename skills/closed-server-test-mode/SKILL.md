---
name: closed-server-test-mode
description: Watchtower kapalı sunucu simülasyonu için test ve QA AI skill'i. Smoke, contract, integration, scenario ve soak testlerini tasarlar; her fazda eklenen parçalar için test kanıtı üretir. Özellikle Wazuh ingest, EventNormalizer, scenario replay ve alert assertion işlerinde kullanılır.
---

# Klasör Ayrımı — Kesinlikle Karıştırılmamalı

- **`watchtower-demo/`** = Bizzat inşa ettiğimiz **ürünün kendisi**. LLM destekli, şirket iç ağını izleyen ve managera uyarı veren CLI sistemi.
- **`server-stack/`** = Bu ürünü test etmek için kurduğumuz **kapalı sunucu ortamı**. Simüle edilmiş şirket ağı (Wazuh, AD, sahte loglar).

Bu skill her iki tarafı test eder: `server-stack` servislerinin ayakta olması + `watchtower-demo`'nun doğru çıktı üretmesi.

---

# Purpose

Bu skill test ve QA odaklı AI içindir.

Ana görev:

- eksik test yüzeyini bulmak
- test dosyaları yazmak
- çalıştırma komutları üretmek
- raporlamak

# Test Öncelikleri

1. contract
2. integration
3. smoke
4. scenario
5. soak

Bir fazda eklenen her şey en az bir test katmanına bağlanmalıdır.

# Watchtower-Özel Test Kuralları

- `WatchtowerEvent` için schema assertion zorunlu.
- `windows-event-bridge` fixture test ister.
- Linux parser için snapshot veya fixture test ister.
- Wazuh ingest için mocked ve gerçek path ayrımı yapılır.
- Scenario testlerinde positive ve negative durum olmalı.
- Alert assertion mümkünse Elasticsearch + CLI üzerinden çift doğrulanır.

# Referanslar

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/close-server-simulation-implementation-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-features-final.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-scenarios-final.md`

# Teslim

```text
TEST KAPSAMI:
YAZILAN TESTLER:
ÇALIŞTIRILAN TESTLER:
SONUÇ:
FAIL VARSA:
EKSİK KALAN YÜZEYLER:
```
