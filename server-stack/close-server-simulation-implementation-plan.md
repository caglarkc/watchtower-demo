# Close Server Simulation — Implementation Plan

> [!IMPORTANT]
> **Klasör Ayrımı — Karıştırılmamalı**
>
> - **`watchtower-demo/`** = Bizzat inşa ettiğimiz **ürünün kendisi**. LLM destekli izleme ve uyarı CLI sistemi.
> - **`server-stack/`** = Bu ürünü test etmek için kurduğumuz **kapalı sunucu ortamı**. Simüle edilmiş şirket ağı.
>
> Bu dosya `server-stack` ortamını adım adım nasıl kuracağımızı açıklar.

**Amaç:** Watchtower için tüm kapalı kurumsal ağı Docker tabanlı olarak sıfırdan kurmak, log akışını entegre etmek, uçtan uca test etmek ve senaryo üretimini doğrulamak için uygulanabilir mühendislik planı.  
**Ana referans:** [watchtower-tool-stack.md](watchtower-tool-stack.md)  
**Destekleyici bağlam:** [watchtower-master-plan.md](../watchtower-master-plan.md), [watchtower-features-final.md](watchtower-features-final.md), [watchtower-scenarios-final.md](watchtower-scenarios-final.md)

---

## 1. Hedef

Bu planın sonunda aşağıdaki durum eksiksiz sağlanmış olmalıdır:

1. Tam kapalı şirket ağı Docker network üzerinde ayağa kalkar.
2. Kimlik, dosya, mail, DB, Git, DNS, ağ ve uygulama logları üretilir.
3. Wazuh + Elasticsearch + Logstash + Filebeat hattı logları ingest eder.
4. Watchtower `security-gateway` ve `analysis-daemon` bu verileri okuyup normalize eder.
5. Hibrit OS simülasyonu `windows-event-bridge` ile desteklenir.
6. Temel ve gelişmiş senaryolar otomatik testlerle tetiklenir.
7. Her faz için deterministik acceptance test ve smoke test komutları bulunur.

---

## 2. Sabit Kapsam

Bu plan aşağıdaki kararları sabit kabul eder:

- Ürün dizini: `watchtower/`
- Simülasyon kökü: `watchtower-demo/`
- İlk SIEM: `Wazuh-only`
- İlk bildirim: `CLI + Telegram`
- Model stratejisi: `OpenAI-compatible abstraction`, kapalı ağ için `local model path` zorunlu
- Faz 1 kapsamı: `login + file + network + AD`
- Mail ve uygulama davranışları: Faz 2'de genişletilir
- Auto-remediation: yok, sadece alert ve öneri

---

## 3. Başarı Kriterleri

Bir implementasyon ancak aşağıdaki koşullar sağlanırsa tamamlanmış sayılır:

- `docker compose up` ile tüm temel servisler temiz şekilde ayağa kalkar.
- Wazuh API sağlıklıdır ve agent kayıtları görünür.
- Elasticsearch indexleri beklenen şemalarla dolar.
- Watchtower en az `Windows path` ve `Linux path` için normalize edilmiş event üretir.
- En az 10 temel feature ve 10 kritik scenario deterministik test ile doğrulanır.
- Faz 1 smoke suite 15 dakika altında tamamlanır.
- Test sonucu aynı seed ile tekrarlandığında aynı ana alert çıktıları oluşur.
- Hiçbir faz, o fazın kendi testleri yeşil olmadan tamamlanmış sayılmaz.

---

## 3.1 Faz Kapanış Kuralı

Bu belgeye göre implementor AI için temel kural şudur:

- Her fazda yapılan **her parça** test edilmelidir.
- "Kod yazıldı" durumu faz tamamlandı anlamına gelmez.
- Bir servis eklendiyse healthcheck + ingest + integration testi zorunludur.
- Bir parser eklendiyse contract test + snapshot test zorunludur.
- Bir senaryo eklendiyse positive + negative replay testi zorunludur.
- Bir CLI komutu eklendiyse command smoke testi zorunludur.

Faz tamamlandı kararı ancak şu sırayla verilir:

1. kod yazıldı
2. ilgili testler yazıldı
3. testler local/demo ortamında çalıştı
4. rapor üretildi
5. manager AI review etti

---

## 3.2 Manager AI Kullanım Şekli

Bu dosya doğrudan kod yazacak AI için değil, öncelikle bir **yönetici AI** için yazılmıştır.

Yönetici AI'nın görevi:

1. Bu belgeyi okuyup fazı seçmek
2. Fazı küçük görevlere bölmek
3. Her görev için alt AI'a net prompt üretmek
4. Doğru referans markdownları prompt'a eklemek
5. Alt AI çıktısını test zorunluluğuna göre review etmek
6. Testsiz işi kabul etmemek

Yönetici AI şu belgeleri görev prompt'larında gerektiği kadar referans göstermelidir:

- [close-server-simulation-implementation-plan.md](close-server-simulation-implementation-plan.md)
- [watchtower-tool-stack.md](watchtower-tool-stack.md)
- [watchtower-master-plan.md](../watchtower-master-plan.md)
- [watchtower-features-final.md](watchtower-features-final.md)
- [watchtower-scenarios-final.md](watchtower-scenarios-final.md)

---

## 3.3 Prompt Orchestration Kuralı

Yönetici AI altındaki kod yazan AI'a görev verirken her prompt içinde şunları zorunlu taşımalıdır:

```text
GÖREV:
FAZ:
ALT HEDEF:
REFERANS DOSYALAR:
ETKİLENECEK DOSYALAR:
YAPILACAKLAR:
TESTLER:
TESLİM KRİTERLERİ:
```

`TESTLER` alanı boş bırakılamaz.

Alt AI'dan istenecek minimum teslim:

- yapılan iş özeti
- değişen dosyalar
- çalışan davranış
- yazdığı testler
- çalıştırdığı testler
- başarısız kalan nokta varsa açık not

---

## 3.4 Alt AI Rol Ayrımı

Bu plan en az dört farklı uzman AI rolünü destekleyecek şekilde düşünülmelidir:

1. **Manager AI**: fazı böler, prompt üretir, review yapar
2. **Infra Builder AI**: Docker, network, config, volumes, healthcheck
3. **Core Coder AI**: watchtower Python kodu, adapters, graph, storage
4. **Test/QA AI**: smoke, integration, scenario, soak testleri

Gerekirse ek roller:

- **Scenario AI**
- **Normalizer AI**
- **Observability Pipeline AI**

---

## 4. Hedef Mimari Bileşenleri

`watchtower-tool-stack.md` içindeki Faz 1-4 sırası korunarak implementasyon yapılacaktır.

Not: Bu belgede geçen `Aşama 0-7` yürütme sırasını anlatır; `watchtower-master-plan.md` içindeki `Faz 0-5` ise ürün/mimari olgunluk katmanlarını anlatır. Manager AI görev üretirken bu iki ekseni birbirine eşitlemeye çalışmamalı, her task'ta her iki etiketi de açıkça yazmalıdır.

### Faz 1 çekirdeği

- Samba4 AD
- Samba File Server
- Wazuh Manager
- Wazuh Agents
- Elasticsearch + Kibana
- Filebeat + Logstash
- DHCP
- User Simulator
- Watchtower core
- `windows-event-bridge`

### Faz 2 genişlemesi

- Postfix + Dovecot + Roundcube
- PostgreSQL + `pg_audit`
- Gitea
- Nginx Gateway
- Zeek

### Faz 3 genişlemesi

- Vault
- Mattermost
- CUPS
- Badge API
- ntopng
- SuiteCRM

### Faz 4 genişlemesi

- 83 senaryo script kütüphanesi
- Composite risk score
- Offboarding / HRIS mock entegrasyonu

---

## 5. Repo ve Dizin Tasarımı

Önerilen yapı:

```text
watchtower/
├── pyproject.toml
├── src/watchtower/
│   ├── cli/
│   ├── config/
│   ├── gateway/
│   ├── graph/
│   ├── normalizers/
│   ├── adapters/
│   ├── storage/
│   ├── alerts/
│   └── tests/
├── scripts/
└── fixtures/

watchtower-demo/
├── docker-compose.yml
├── .env.example
├── configs/
│   ├── wazuh/
│   ├── logstash/
│   ├── filebeat/
│   ├── samba/
│   ├── postgres/
│   ├── zeek/
│   └── nginx/
├── simulation/
│   ├── event_generator/
│   ├── scenarios/
│   ├── badge_api/
│   ├── windows_event_bridge.py
│   └── seeds/
├── tests/
│   ├── smoke/
│   ├── integration/
│   ├── scenario/
│   └── fixtures/
└── reports/
```

---

## 6. Uygulama Sırası

### Aşama 0: Tasarım freeze

- `watchtower-tool-stack.md` içindeki servis listesini implementation backlog'a çevir
- Ortak alanları sabitle: `user`, `timestamp`, `source_ip`, `source_os`, `event_type`
- Elasticsearch index adlarını Bölüm 13 ile birebir eşle
- `WatchtowerEvent` şemasını yazılı sözleşme haline getir

### Aşama 1: Altyapı iskeleti

- `watchtower/` Python paketini oluştur
- CLI komutlarını iskeletle: `wt status`, `wt alerts`, `wt rules`, `wt learning`
- SQLite store'ları oluştur: `rules.db`, `baseline.db`, `alerts.db`
- `security-gateway` ve `analysis-daemon` process boundary’sini ayır

### Aşama 2: Demo network kurulumu

- `corp-lan` Docker ağı ve statik IP planını oluştur
- `docker-compose.yml` içine önce Faz 1 servislerini ekle
- Healthcheck, volume, restart policy ve bağımlılık ağacını tamamla
- Her servis için config mount ve seed data volume hazırla

### Aşama 3: Log ingestion hattı

- Wazuh Manager kurulumu
- Elasticsearch + Kibana kurulumu
- Logstash pipeline ve Filebeat input/output mapping
- Wazuh alert index ve custom app log indexlerinin doğrulanması

### Aşama 4: Hibrit OS normalizasyonu

- `windows-event-bridge` ile Samba AD loglarını `Event ID` benzeri yapıya çevir
- Linux audit/syslog/JSON parser’larını yaz
- `EventNormalizer` node’unu iki giriş yoluyla test et
- Ortak `WatchtowerEvent` çıktısını snapshot test ile sabitle

### Aşama 5: Watchtower çekirdeği

- Wazuh REST adapter
- Elasticsearch query adapter
- LangGraph node zinciri
- Rule Store lifecycle
- Learning mode state machine
- Severity engine v1

### Aşama 6: Senaryo üretim sistemi

- Deterministic `event_generator`
- Role-based user seed’leri
- Temel senaryo DSL veya YAML tanımı
- Senaryo başlatma komutları: `run_scenario <id>`

### Aşama 7: Test otomasyonu

- Container smoke test
- Adapter integration test
- Normalizer contract test
- Scenario replay test
- Alert assertion test

Her aşamanın sonunda manager AI şu soruyu kapatmadan fazı ilerletmez:

- "Bu aşamada eklenen her şey için çalışan test kanıtı var mı?"

---

## 7. WatchtowerEvent Sözleşmesi

İlk sürüm için minimum normalized event:

```json
{
  "event_id": "uuid",
  "timestamp": "2026-05-22T03:47:00Z",
  "user": "ali.koc",
  "source_ip": "10.0.2.15",
  "source_host": "WS-ALIKOC-01",
  "source_os": "windows|linux",
  "event_type": "login_success|login_failed|file_access|group_change|process_create|network_connect",
  "target": "HR-DB-01",
  "severity_hint": "low|medium|high",
  "raw_ref": "index/id",
  "attributes": {}
}
```

Bu sözleşme değişirse:

- normalizer testleri,
- correlation testleri,
- scenario assertion fixture’ları

aynı commit içinde güncellenmek zorundadır.

---

## 8. Docker Compose Tasarım Kuralları

Her servis için aşağıdakiler zorunludur:

- sabit servis adı
- sabit IP
- `healthcheck`
- persistent volume
- log output strategy
- minimal config override
- deterministic boot order

Zorunlu compose bölümleri:

- `networks`
- `volumes`
- `x-health-defaults` benzeri tekrar azaltıcı anchor yapıları
- `depends_on` + health şartları

Örnek servis gruplaması:

- `identity`: samba-ad, openldap
- `observability`: wazuh, elasticsearch, kibana, filebeat, logstash
- `business`: postfix, dovecot, postgres, gitea, nginx, suitecrm
- `simulation`: badge-api, user-simulator, windows-event-bridge
- `watchtower`: security-gateway, analysis-daemon

---

## 9. Konfigürasyon Yönetimi

Her servis için üç katmanlı config yaklaşımı kullanılmalı:

1. `base config`
2. `demo override`
3. `test override`

Örnek:

- `configs/logstash/base/pipeline.conf`
- `configs/logstash/demo/pipeline.override.conf`
- `configs/logstash/test/pipeline.override.conf`

Zorunlu `.env` alanları:

- `TZ`
- `WATCHTOWER_MODE`
- `ELASTICSEARCH_URL`
- `WAZUH_API_URL`
- `WAZUH_API_USER`
- `WAZUH_API_PASSWORD`
- `WATCHTOWER_LOCAL_MODEL_URL`
- `WATCHTOWER_FAST_MODEL`
- `WATCHTOWER_POWER_MODEL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

---

## 10. Test Stratejisi

### Test katmanları

1. `unit`
2. `contract`
3. `integration`
4. `scenario`
5. `smoke`
6. `soak`

Temel kural:

- Her implementasyon görevi en az bir test katmanına bağlanmalıdır.
- Teste bağlanmayan iş kabul edilmez.

### 10.1 Unit test

Kapsam:

- field mapping
- event classification helpers
- severity score calculation
- baseline update functions
- Rule Store lifecycle

### 10.2 Contract test

Kapsam:

- Wazuh alert JSON → internal adapter contract
- Samba audit → windows bridge contract
- auditd/syslog → linux parser contract
- `WatchtowerEvent` JSON schema validation

### 10.3 Integration test

Kapsam:

- Wazuh API erişimi
- Elasticsearch indexleme
- Logstash pipeline parsing
- Filebeat shipping
- `security-gateway` query path
- `analysis-daemon` ingest path

### 10.4 Scenario test

Kapsam:

- 1 senaryo → 1 veya daha fazla beklenen alert
- negative case: normal davranışta alert çıkmaması
- repeated replay: duplicate suppression davranışı

### 10.5 Smoke test

Kapsam:

- servislerin ayağa kalkması
- ingest hattının canlı olması
- örnek login event üretimi
- örnek file access event üretimi
- `wt status` sağlığı

### 10.6 Soak test

Kapsam:

- 6-12 saat sürekli event akışı
- resource leak
- Elasticsearch disk büyümesi
- baseline drift dayanıklılığı

---

## 11. Faz Bazlı Test Planı

Her faz için manager AI görev bölmeden önce şu matrisi doldurmuş kabul etmelidir:

- hangi servis ekleniyor
- hangi parser/adapter ekleniyor
- hangi CLI veya daemon davranışı ekleniyor
- bunun unit testi ne
- bunun integration testi ne
- bunun smoke testi ne
- varsa scenario testi ne

### Faz 1 testleri

- AD login success/failure
- SMB file read volume anomaly
- DHCP lease map doğrulama
- Wazuh alert ingest
- Windows path normalizasyonu
- Linux path normalizasyonu

### Faz 2 testleri

- mail send volume anomaly
- mailbox access anomaly
- Postgres bulk select anomaly
- Gitea mass clone anomaly
- Nginx 401/403 spike anomaly
- Zeek east-west traffic anomaly

### Faz 3 testleri

- Vault secret burst
- Mattermost credential pattern
- CUPS unusual print
- badge + login impossible travel
- ntopng high-volume east-west

### Faz 4 testleri

- 83 scenario replay coverage
- feature-to-scenario matrix coverage
- composite risk score stability

---

## 11.1 Faz Bazlı AI Çalışma Protokolü

Her faz aşağıdaki rollerle ilerler:

### Faz başlangıcı

- Manager AI faz hedefini seçer
- Bu belgeden ilgili bölüm numaralarını referans alır
- Alt görevleri 1-4 küçük prompt'a böler

### Faz implementasyonu

- Infra ile ilgili işler Infra Builder AI'a gider
- Python core ile ilgili işler Core Coder AI'a gider
- Test harness işleri Test/QA AI'a gider
- Senaryo replay işleri Scenario AI'a gider

### Faz review

- Manager AI teslimleri toplar
- Test kanıtı olmayan işi geri çevirir
- Gerekirse revize prompt üretir
- Ancak tüm kapılar yeşilse bir sonraki faza geçer

---

## 12. Feature Coverage Gate

Her feature için aşağıdaki artefact zorunludur:

- kaynak log örneği
- parser veya adapter
- normalized event örneği
- positive test
- negative test
- alert expectation

Minimum Phase 1 gate:

- `F-001`
- `F-006`
- `F-007`
- `F-008`
- `F-009`
- `F-010`
- `F-014`
- `F-020`
- `F-021`
- `F-028` veya eşdeğer network-access feature

---

## 13. Scenario Coverage Gate

İlk zorunlu senaryolar:

- `S-002`
- `S-004`
- `S-006`
- `S-016`
- `S-018`
- `S-019`
- `S-020`
- `S-021`
- `S-030`
- `S-034`

Bu ilk set:

- veri sızdırma
- credential abuse
- privilege change
- network ve endpoint korelasyonu

alanlarını birlikte doğrulamalıdır.

---

## 14. Uçtan Uca Çalıştırma Akışı

### Adım 1

- `.env` üret
- volume klasörlerini hazırla
- sertifika ve demo credential seed’lerini yaz

### Adım 2

- observability servislerini ayağa kaldır
- Wazuh, Elasticsearch, Kibana health kontrolü yap

### Adım 3

- identity ve file servislerini ayağa kaldır
- agent registration ve log shipping doğrula

### Adım 4

- Watchtower `security-gateway` ve `analysis-daemon` başlat
- `wt status` ve `wt rules list` doğrula

### Adım 5

- user simulator ile normal davranış seed’i çalıştır
- learning-mode ingestion doğrula

### Adım 6

- tekil scenario replay çalıştır
- alert assertion ve index assertion yap

### Adım 7

- smoke suite
- integration suite
- selected scenario suite

---

## 15. Komut Yüzeyi

Planlanan komutlar:

```bash
# demo altyapısını başlat
docker compose up -d

# sağlık kontrolü
docker compose ps
wt status

# normal seed
make seed-baseline

# tekil senaryo replay
make scenario SCENARIO=S-016

# Faz 1 smoke
make test-smoke

# entegrasyon testleri
make test-integration

# senaryo testleri
make test-scenarios

# tam regression
make test-all
```

---

## 16. Test Araçları

Önerilen araçlar:

- `pytest`
- `pytest-asyncio`
- `testcontainers` veya docker compose tabanlı fixture yönetimi
- `schemathesis` gerekirse API contract için
- `jsonschema`
- `freezegun`
- `factory-boy` veya custom fixture builder

Log doğrulama için:

- Elasticsearch query helper
- Wazuh alert poll helper
- SQLite assertion helper
- Telegram mock sink

---

## 17. Gözlemlenebilirlik ve Raporlama

Test sonunda otomatik üretilmesi gereken raporlar:

- servis sağlık raporu
- container boot süresi
- index dolum raporu
- normalize event sayısı
- alert sayısı
- scenario başına başarı durumu
- flaky test raporu

Rapor dizini:

```text
watchtower-demo/reports/
├── smoke/
├── integration/
├── scenario/
└── soak/
```

---

## 18. Riskler ve Koruyucu Önlemler

### Teknik riskler

- Wazuh boot karmaşıklığı
- Elasticsearch kaynak tüketimi
- Logstash parser drift
- deterministik olmayan scenario üretimi
- LLM bağımlılığı nedeniyle test nondeterminism

### Önlemler

- tüm LLM node’ları için test modunda mock veya recorded response seçeneği
- scenario seed’leri için sabit random seed
- healthcheck timeout ve retry standardı
- her parser için fixture snapshot
- ağır servisleri fazlara bölerek ayağa kaldırma

---

## 19. Acceptance Checklist

Tamamlandı demek için hepsi işaretlenmiş olmalı:

- [ ] Compose dosyası tüm Faz 1 servisleriyle çalışıyor
- [ ] Wazuh agent kayıtları sağlıklı
- [ ] Elasticsearch indexleri beklenen alanları içeriyor
- [ ] `windows-event-bridge` beklenen `Event ID` dönüşümlerini üretiyor
- [ ] Linux parser `auditd/syslog/JSON` akışlarını parse ediyor
- [ ] `EventNormalizer` iki yolu tek şemada birleştiriyor
- [ ] Watchtower learning mode veri topluyor
- [ ] En az 10 feature testten geçiyor
- [ ] En az 10 scenario testten geçiyor
- [ ] Telegram mock veya gerçek sink ile alert doğrulanıyor
- [ ] `wt status` ve temel CLI komutları çalışıyor
- [ ] Smoke suite yeşil
- [ ] Integration suite yeşil
- [ ] Scenario suite seçili set için yeşil

---

## 20. Uygulama İş Paketi Sırası

Bu plan doğrudan backlog'a şu sırayla çevrilmelidir:

1. `watchtower/` package scaffold
2. `watchtower-demo/docker-compose.yml` Faz 1 iskeleti
3. Wazuh + Elasticsearch boot ve healthcheck
4. Samba AD + File Server + log shipping
5. `windows-event-bridge`
6. Watchtower normalizer contracts
7. Wazuh adapter + Elasticsearch adapter
8. LangGraph ingest → normalize → baseline pipeline
9. User simulator baseline mode
10. Scenario runner
11. Smoke/integration/scenario tests
12. Faz 2 genişleme servisleri

---

## 21. Net Sonuç

Bu planın amacı sadece mimari açıklama değildir. Bu belge, `watchtower-tool-stack.md` içinde tanımlanan tüm kapalı sunucu simülasyon yapısını:

- kurulur,
- entegre edilir,
- test edilir,
- tekrar çalıştırılır,
- regression'a sokulur

hale getirecek operasyonel uygulama planıdır.

İmplementasyon sırasında kural şudur:

- önce Faz 1'i yeşil yap,
- sonra Faz 2 servislerini ekle,
- ardından scenario kütüphanesini büyüt,
- en son soak ve tam regression seviyesine çık.
