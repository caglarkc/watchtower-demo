# Close Server Simulation — Mac-First Implementation Plan

> [!IMPORTANT]
> **Klasör Ayrımı — Karıştırılmamalı**
>
> - **`watchtower-demo/`** = Bizzat inşa ettiğimiz **ürünün kendisi**. LLM destekli izleme ve uyarı CLI sistemi.
> - **`server-stack/`** = Bu ürünü test etmek için kurduğumuz **kapalı sunucu ortamı**. Simüle edilmiş şirket ağı.
>
> Bu dosya `server-stack` ortamını Mac üzerinde geliştirme önceliğiyle nasıl kuracağımızı açıklar.

**Amaç:** Mevcut implementasyon planını koruyarak, geliştirme işinin öncelikle macOS üzerinde yapılacağı; fakat ürün doğrulamasının Ubuntu ve Windows davranışlarını kapsayacak şekilde tasarlanacağı ikinci bir yürütme planı oluşturmak.

**Bu belge neyi değiştirir:** Kodlama ve günlük geliştirme akışını `Mac-first` kabul eder.
**Bu belge neyi değiştirmez:** Ana ürün kapsamı, faz yapısı, acceptance kriterleri ve hibrit OS gereklilikleri aynen korunur.

**Ana referanslar:**
- [close-server-simulation-implementation-plan.md](close-server-simulation-implementation-plan.md)
- [watchtower-master-plan.md](../watchtower-master-plan.md)
- [watchtower-tool-stack.md](watchtower-tool-stack.md)
- [watchtower-features-final.md](watchtower-features-final.md)
- [watchtower-scenarios-final.md](watchtower-scenarios-final.md)

---

## 1. Bu Planın Pozisyonu

Bu belge, mevcut ana planın yerine geçmez. Amaç:

1. Ana planı `source of truth` olarak bırakmak
2. Mac üzerinde üretken geliştirme akışını netleştirmek
3. Ubuntu ve Windows kapsamını test stratejisinde görünür kılmak
4. Gerekirse ileride ayrı bir `Ubuntu-first` uygulama akışına geri dönebilmeyi kolaylaştırmak

Kural:

- Ürün kararı için ana plan esas alınır
- Günlük geliştirme akışı için bu belge esas alınır
- İki belge çelişirse ürün kapsamı tarafında ana plan kazanır

Adlandırma notu: Bu belgede geçen `Faz 0-7`, uygulama akışındaki yürütme adımları içindir. `watchtower-master-plan.md` içindeki `Faz 0-5` ise ürün yetenek seviyelerini anlatır. Görev çıkarırken iki etiket birlikte yazılmalıdır.

---

## 2. Temel Varsayım

Bu varyantta çalışma modeli şöyledir:

- Kodlama ortamı: `macOS`
- Günlük servis ayağa kaldırma: öncelikle `Docker Desktop` veya eşdeğer Mac Docker kurulumu
- İlk test yazımı: Mac üzerinde
- İlk tam doğrulama ortamı: `Ubuntu`
- Windows kapsamı: gerçek Windows telemetry yerine önce `fixture + bridge + replay` ile garanti altına alınır

Bu yüzden hedefimiz:

- Mac'te hızlı geliştirme
- Ubuntu'da güvenilir entegrasyon doğrulaması
- Windows path için deterministik contract/integration kapsamı

---

## 3. Değişmeyen Ürün Gerçekleri

Bu belge aşağıdaki gerçekleri değiştirmez:

- Sistem hibrit OS mantığıyla tasarlanacaktır
- `Windows path` ve `Linux path` ayrı normalizasyon yolları olarak korunacaktır
- Faz 1 için `Wazuh-only` ingest yaklaşımı korunacaktır
- Her fazın kapanışı test kanıtına bağlı olacaktır
- `contract`, `integration`, `scenario` ve `smoke` testleri zorunlu kalacaktır

Özellikle:

- `Windows Event ID` tabanlı kimlik/erişim olayları
- `auditd/syslog/JSON` tabanlı Linux servis olayları

aynı ürün sözleşmesinin parçası olmaya devam eder.

---

## 4. Mac-First Geliştirme Prensipleri

### 4.1 Ana fikir

Mac üzerinde tüm sistemi birebir üretim eşleniği gibi doğrulamaya çalışmak yerine:

- ürün iskeleti
- parser/normalizer mantığı
- CLI
- adapter katmanı
- senaryo altyapısı
- Linux ağırlıklı container entegrasyonu

ilk etapta Mac'te geliştirilir.

### 4.2 Mac'te güvenle yapılabilecek işler

- Python package scaffold
- CLI iskeleti ve komut testleri
- SQLite store ve state machine geliştirmesi
- Fixture tabanlı parser ve normalizer testleri
- Docker compose düzeni
- Linux servisleriyle integration testlerin büyük kısmı
- Scenario runner ve deterministic seed sistemi

### 4.3 Mac'te sınırlı güvenle yapılacak işler

- Wazuh/Elasticsearch ağır stack boot davranışı
- Windows event davranışının gerçek dünyaya yakınlığı
- dosya sistemi, line ending ve shell farkları
- gerçek Linux network ve service startup edge-case'leri

Bu alanlar Mac'te tamamen bitmiş kabul edilmez; Ubuntu doğrulaması beklenir.

---

## 5. Platform Sorumluluk Matrisi

### 5.1 macOS

Amaç:

- ana geliştirme ortamı
- hızlı iterasyon
- test yazımı
- compose/topoloji tasarımı

Mac zorunlu kapsamı:

- `unit`
- `contract`
- CLI `smoke`
- hafif `integration`
- scenario fixture hazırlığı

### 5.2 Ubuntu

Amaç:

- gerçek entegrasyon doğrulaması
- container davranışı doğrulaması
- boot order ve healthcheck doğrulaması
- tam regression

Ubuntu zorunlu kapsamı:

- full `integration`
- selected `scenario`
- `smoke`
- compose boot/doğrulama
- log shipping ve index kontrolü

### 5.3 Windows kapsamı

Amaç:

- gerçek Windows bağımlılığı olmayan erken güvence
- normalizer ve bridge davranışının deterministik testi

Windows için ilk faz yaklaşımı:

- recorded event fixture
- `windows-event-bridge` contract testi
- replay tabanlı integration testi

Windows için daha ileri doğrulama:

- gerektiğinde ayrı VM veya runner üzerinde gerçek event üretimi

---

## 6. Fazların Mac-First Yorumu

### Faz 0: Tasarım freeze

Mac üzerinde yapılır.

Teslim:

- `WatchtowerEvent` sözleşmesi
- klasör yapısı kararı
- test klasör hiyerarşisi
- compose servis sınırları

Zorunlu test:

- henüz runtime test değil
- schema validation örneği ve fixture taslakları hazırlanır

### Faz 1: Altyapı iskeleti

Mac üzerinde başlanır.

Yapılacaklar:

- `watchtower/` package scaffold
- temel CLI komutları
- SQLite store katmanları
- config yükleme mekanizması

Mac kapanış şartı:

- temel unit testler
- CLI smoke testleri

Ubuntu kapanış şartı:

- paket kurulumu ve komutların temiz çalışması

### Faz 2: Demo network kurulumu

Mac üzerinde compose iskeleti yazılır, Ubuntu'da sert doğrulanır.

Yapılacaklar:

- `docker-compose.yml`
- network, volume, healthcheck
- Faz 1 servisleri için config mount yapısı

Mac kapanış şartı:

- compose lint mantığı
- hafif servis smoke

Ubuntu kapanış şartı:

- `docker compose up -d`
- servis healthcheck doğrulaması
- boot sırası sorunlarının çözülmesi

### Faz 3: Log ingestion hattı

Mac'te geliştirilir, Ubuntu'da gerçek doğrulama yapılır.

Yapılacaklar:

- Wazuh
- Elasticsearch
- Logstash
- Filebeat mapping

Mac kapanış şartı:

- config doğrulama
- parser fixture testleri
- mümkün olan container smoke

Ubuntu kapanış şartı:

- ingest gerçekten akıyor mu
- indexler doluyor mu
- alert/path doğrulanıyor mu

### Faz 4: Hibrit OS normalizasyonu

Bu faz Mac için en uygun geliştirme fazlarından biridir.

Yapılacaklar:

- Windows fixture setleri
- Linux fixture setleri
- `windows-event-bridge`
- Linux parser'ları
- ortak `EventNormalizer`

Mac kapanış şartı:

- contract test
- snapshot test
- schema validation

Ubuntu kapanış şartı:

- replay ile iki yolun da entegrasyon doğrulaması

### Faz 5: Watchtower çekirdeği

Mac'te ağırlıklı geliştirilir.

Yapılacaklar:

- adapter'lar
- graph/pipeline
- rule store lifecycle
- learning mode
- severity engine

Mac kapanış şartı:

- unit test
- adapter contract
- selected integration

Ubuntu kapanış şartı:

- Wazuh ve Elasticsearch ile uçtan uca çalışması

### Faz 6: Senaryo üretim sistemi

Mac'te yazılır, Ubuntu'da kabul testine girer.

Yapılacaklar:

- deterministic event generator
- user seed'leri
- scenario DSL/YAML
- scenario runner

Mac kapanış şartı:

- senaryo fixture üretimi
- scenario unit ve replay testleri

Ubuntu kapanış şartı:

- seçili Faz 1 senaryoları yeşil

### Faz 7: Test otomasyonu

Bu faz en sona bırakılmaz; önceki fazlarla paralel büyütülür.

Mac sorumluluğu:

- test harness yazımı
- fixture builder
- local smoke

Ubuntu sorumluluğu:

- full matrix doğrulama
- integration ve scenario regression

---

## 7. Test Yazım Zamanlaması

Bu varyantta testler tamamen sona bırakılmaz. Kural:

- Her büyük yapı parçası Mac'te yazılırken en az bir testle birlikte gelir
- Ağır entegrasyon doğrulaması Ubuntu'ya bırakılabilir
- Ama testsiz mimari parça kabul edilmez

Örnek:

- parser yazıldıysa aynı gün contract testi yazılır
- CLI komutu yazıldıysa aynı committe smoke testi gelir
- scenario runner yazıldıysa en az bir replay testi gelir

---

## 8. Önerilen Test Ayrımı

### 8.1 Mac'te koşulacak testler

- `pytest tests/unit`
- `pytest tests/contract`
- `pytest tests/cli`
- hafif `integration` alt kümesi

### 8.2 Ubuntu'da koşulacak testler

- `pytest tests/integration`
- `pytest tests/scenarios`
- compose boot smoke
- healthcheck ve shipping doğrulaması

### 8.3 Windows davranışı için yazılacak testler

- `tests/contract/windows`
- `tests/integration/windows_bridge`
- Event ID fixture replay seti

---

## 9. Repo Yapısına Ek Öneri

Ana planı bozmadan şu test ayrımı eklenmelidir:

```text
tests/
├── unit/
├── contract/
│   ├── windows/
│   └── linux/
├── cli/
├── integration/
│   ├── linux_stack/
│   └── windows_bridge/
└── scenarios/
    └── phase1/
```

Fixture önerisi:

```text
fixtures/
├── windows/
├── linux/
├── wazuh/
└── scenarios/
```

---

## 10. Mac-First Riskler

### Risk 1

Mac'te çalışan compose davranışı Ubuntu'da farklılaşabilir.

Önlem:

- Ubuntu doğrulamasını ayrı faz sonu kapısı yapmak

### Risk 2

Windows path gerçekte test edilmeden fazla güvenilebilir.

Önlem:

- Windows fixture kalitesini yüksek tutmak
- bridge contract ve snapshot testlerini zorunlu yapmak

### Risk 3

Testler ertelenirse büyük entegrasyon borcu birikir.

Önlem:

- her fazda minimum Mac testi zorunlu
- Ubuntu full run birikimli değil, düzenli yapılmalı

### Risk 4

Wazuh/Elasticsearch gibi ağır servisler Mac kaynaklarını zorlayabilir.

Önlem:

- local geliştirmede minimal servis profilleri
- full stack doğrulamayı Ubuntu'ya taşıma

---

## 11. Faz Kapanış Kuralları Bu Varyantta Nasıl Okunmalı

Bir fazın gerçekten kapanması için iki ayrı durum izlenmelidir:

1. `Mac development gate`
2. `Ubuntu verification gate`

Mac development gate:

- ilgili kod yazıldı
- ilgili hafif testler yazıldı
- local ortamda temel davranış doğrulandı

Ubuntu verification gate:

- integration veya smoke karşılığı çalıştı
- container ve ingest davranışı doğrulandı
- fazın platform riskleri kapatıldı

Not:

- Faz teknik olarak Mac'te "implement edildi" denebilir
- Ama ürün açısından "tamamlandı" demek için Ubuntu kapısı da geçilmelidir

---

## 12. Hangi Durumda Bu Plan Kullanılmalı

Bu belge şu durumlar için uygundur:

- ana geliştirme makinesi Mac ise
- Linux hedefi korunuyorsa
- Windows telemetry kapsamı tamamen atlanmak istenmiyorsa
- proje hızlı ilerlesin ama platform riski görünür kalsın isteniyorsa

Bu belge şu durumlarda yeterli değildir:

- doğrudan production benzeri Linux kurulum isteniyorsa
- gerçek Windows host üzerinden erken doğrulama zorunluysa

---

## 13. Net Sonuç

Bu varyantın özeti:

- geliştirme `Mac-first`
- ürün doğrulaması `Ubuntu-first`
- ürün kapsamı `Windows + Linux path`
- ana plan korunur
- bu belge yalnızca yürütme ve testleme sırasını platforma göre yeniden düzenler

En önemli prensip:

- Mac'te rahat geliştir
- Ubuntu'da gerçekten doğrula
- Windows path'i fixture ve bridge testleriyle erkenden güvenceye al
