---
name: closed-server-infra-builder-mode
description: Watchtower kapalı sunucu simülasyonu için Docker ve servis altyapısını kuran AI skill'i. Compose, network, volumes, config mount, healthcheck, Wazuh/Elastic/Logstash/Filebeat/Samba/Postfix/Gitea gibi servisleri fazlara göre kurar ve her servis için smoke ve integration testi bekler.
---

# Purpose

Bu skill kapalı şirket ağını kuran infra AI içindir.

Kapsam:

- `docker-compose.yml`
- `configs/`
- service healthchecks
- static IP planı
- volumes
- env dosyaları
- boot order

# Rules

- Her servis için sabit isim, sabit IP, healthcheck, volume ve config mount olmalı.
- Faz 1 dışına taşan servis ekleniyorsa gerekçesi yazılmalı.
- Compose değişikliği test edilmeden teslim edilmez.
- `depends_on` sadece boot için değil health koşullarıyla düşünülür.
- Secret değerleri hardcode etme; `.env.example` veya env referansı kullan.

# Zorunlu Testler

Her görevde bunlardan uygun olanları iste:

- container boot testi
- healthcheck doğrulaması
- port erişim testi
- network reachability testi
- log shipping testi
- persistence testi

# Referanslar

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/close-server-simulation-implementation-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-tool-stack.md`

# Teslim

```text
YAPILAN İŞ:
DEĞİŞEN DOSYALAR:
AYAĞA KALKAN SERVİSLER:
YAZILAN/ÇALIŞTIRILAN TESTLER:
BEKLENEN ENV VE CONFIG:
RİSKLER:
```
