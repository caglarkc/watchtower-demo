---
name: closed-server-code-mode
description: Watchtower kapalı sunucu simülasyonu için core kod yazan AI skill'i. Manager AI'dan gelen görev prompt'unu uygular; Wazuh adapter, LangGraph pipeline, normalizer, gateway, storage ve CLI parçalarını mimariye uygun yazar. Her görevde test veya manuel doğrulama kanıtı üretir.
---

# Klasör Ayrımı — Kesinlikle Karıştırılmamalı

- **`watchtower-demo/`** = Bizzat inşa ettiğimiz **ürünün kendisi**. LLM destekli, şirket iç ağını izleyen ve managera uyarı veren CLI sistemi.
- **`server-stack/`** = Bu ürünü test etmek için kurduğumuz **kapalı sunucu ortamı**. Simüle edilmiş şirket ağı (Wazuh, AD, sahte loglar).

Bu skill `watchtower-demo/` tarafında — yani **ürün kodunda** — çalışır.

---

# Purpose

Bu skill Watchtower tarafında kod yazan uygulayıcı AI içindir.

Kapsam:

- `watchtower/` Python kodu
- adapters
- normalizers
- graph
- storage
- CLI
- alert ve baseline mantığı

# Görev Alımı

Görev şu başlıklarla gelmelidir:

```text
GÖREV:
FAZ:
ROL:
REFERANSLAR:
ETKİLENECEK DOSYALAR:
YAPILACAK:
TESTLER:
TESLİM KRİTERLERİ:
```

`TESTLER` alanı yoksa görev eksiktir; not düş.

# Rules

- Kod yazmadan önce 4 başlık ver:

```text
NE İSTENDİ:
HANGİ DOSYALAR ETKİLENECEK:
RİSKLER:
YAPILACAKLAR:
```

- Async I/O zorunlu.
- Type hint zorunlu.
- Dış bağlantılar try/except ile korunur.
- Yeni dependency gerekiyorsa sadece not düş.
- Kendi dosya sahipliği dışına yazma.
- Test istenmişse test yaz; en azından çalıştırma planını bırakma, mümkünse gerçek test ekle.
- Normalizer ve adapter işlerinde fixture bazlı assertion düşün.

# Watchtower-Özel Kurallar

- `WatchtowerEvent` sözleşmesini bozma.
- `windows` ve `linux` log path’leri ayrı parse edilir, ortak şemada birleşir.
- Wazuh-first yaklaşımını koru.
- Faz 1'de mail kaynaklarını core akışa zorla sokma.
- Rule Store statüleri: `pending`, `stable`, `deleted`

# Zorunlu Referanslar

- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/close-server-simulation-implementation-plan.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-tool-stack.md`
- `/home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/watchtower-master-plan.md`

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

MANUEL KONTROL:
- ...

NOTLAR:
- ...
```
