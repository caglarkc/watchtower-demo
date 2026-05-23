# Closed Server Simulation — Implementation Plan

> [!IMPORTANT]
> **Klasör Ayrımı — Karıştırılmamalı**
>
> - **`watchtower-demo/`** = Watchtower ürün ailesinin repo kökü.
> - **`watchtower-demo/server-stack/`** = Bu dokümanın kapsamı olan kapalı şirket ağı simülasyonu.
>
> Bu plan **Watchtower gözlemleme ürününü yazmaz**. `src/watchtower`, CLI, adapter,
> normalizer, alert engine, Telegram veya LLM entegrasyonu bu planın kapsamı değildir.
> Bu plan yalnızca kapalı sunucu ortamını kurar, feature davranışlarını simüle eder
> ve çalıştığını test kanıtı ile doğrular.

**Amaç:** `watchtower-features-final.md` içindeki 81 feature ve
`watchtower-scenarios-final.md` içindeki 83 senaryonun kapalı LAN içinde
simüle edilebilir olmasını sağlamak.

**Ana referanslar:**

- [watchtower-tool-stack.md](watchtower-tool-stack.md)
- [watchtower-features-final.md](watchtower-features-final.md)
- [watchtower-scenarios-final.md](watchtower-scenarios-final.md)

---

## 1. Net Kapsam

Bu dosya kod yazacak AI için faz bazlı kontrol dokümanıdır.

Yapılacaklar:

1. Docker tabanlı kapalı şirket ağı kurulacak.
2. Kimlik, dosya, mail, DB, Git, DNS, DHCP, proxy, ağ, endpoint, badge, HR ve uygulama davranışları üretilecek.
3. Her feature için simülasyon yolu tanımlanacak.
4. Her feature için pozitif ve negatif test kanıtı üretilecek.
5. 83 senaryo replay edilebilir hale getirilecek.
6. Test sonunda coverage raporu üretilecek.

Yapılmayacaklar:

- Watchtower ürün kodu yazılmayacak.
- `security-gateway`, `analysis-daemon`, LangGraph pipeline, alert engine veya LLM entegrasyonu kurulmayacak.
- Simülasyon başarısı Watchtower çıktısına bağlanmayacak.
- Telegram, Slack, e-posta alarmı veya manager notification kabul kriteri olmayacak.

Bu planda geçen Wazuh, Elasticsearch, Logstash ve Filebeat yalnızca
**server-stack içindeki log üretim/toplama doğrulama araçlarıdır**. Watchtower
gözlemleme ürünü değildir.

---

## 2. Başarı Kriterleri

Bir faz ancak aşağıdaki kanıtlarla tamamlanmış sayılır:

- `docker compose config` hatasız çalışır.
- Faz servisleri `docker compose up -d` ile ayağa kalkar veya ortam yetersizse gerçek hata çıktısı raporlanır.
- Eklenen her servis için healthcheck veya eşdeğer smoke kontrolü vardır.
- Eklenen her feature için en az bir simülasyon komutu vardır.
- Eklenen her feature için pozitif test vardır.
- Eklenen her feature için negatif kontrol vardır veya neden ertelendiği açıkça yazılmıştır.
- Her scenario replay aynı seed ile deterministik çıktı üretir.
- Raporlar `watchtower-demo/server-stack/reports/` altına yazılır.

Testsiz teslim kabul edilmez.

---

## 3. Simülasyon İlkeleri

Her feature üç simülasyon tipinden biriyle karşılanabilir:

| Tip | Anlam | Kabul koşulu |
| --- | --- | --- |
| `service-backed` | Gerçek container servisi olay üretir | Servis health + log üretimi + test |
| `synthetic-log` | Gerçek servis ağır veya gereksizdir; fixture/log generator olay üretir | Deterministik fixture + schema/field test |
| `hybrid` | Servis var, bazı edge eventler script ile enjekte edilir | Servis health + replay + log assertion |

Her feature için zorunlu metadata:

```yaml
feature_id: F-001
category: network
phase: 1
simulation_type: service-backed|synthetic-log|hybrid
services:
  - samba-file
log_sources:
  - samba_audit
  - zeek_conn
positive_replay: make feature FEATURE=F-001
negative_replay: make feature-negative FEATURE=F-001
evidence:
  - reports/features/F-001.json
```

---

## 4. Dizin Tasarımı

Kod yazacak AI bu yapıyı hedeflemelidir:

```text
watchtower-demo/server-stack/
├── docker-compose.yml
├── .env.example
├── Makefile
├── configs/
│   ├── samba/
│   ├── wazuh/
│   ├── elasticsearch/
│   ├── logstash/
│   ├── filebeat/
│   ├── bind/
│   ├── dhcp/
│   ├── postfix/
│   ├── dovecot/
│   ├── roundcube/
│   ├── postgres/
│   ├── gitea/
│   ├── nginx/
│   ├── zeek/
│   ├── vault/
│   ├── mattermost/
│   ├── cups/
│   ├── proxy/
│   └── suitecrm/
├── simulation/
│   ├── event_generator/
│   ├── feature_catalog/
│   ├── feature_replays/
│   ├── scenarios/
│   ├── seeds/
│   ├── badge_api/
│   ├── hris_mock/
│   ├── ai_gateway_mock/
│   ├── proxy_sink/
│   └── fixtures/
├── tests/
│   ├── smoke/
│   ├── integration/
│   ├── feature/
│   ├── scenario/
│   └── fixtures/
└── reports/
    ├── smoke/
    ├── integration/
    ├── features/
    ├── scenarios/
    └── coverage/
```

`watchtower-demo/src/watchtower/` bu planın dışındadır.

---

## 5. Fazlar

### Faz 0 — Feature Coverage Freeze

Hedef:

- 81 feature listesini makine okunur coverage manifestine çevirmek.
- 83 scenario listesini makine okunur scenario manifestine çevirmek.
- Her feature için faz, servis, log kaynağı ve test komutu alanlarını tanımlamak.

Etkilenecek dosyalar:

- `simulation/feature_catalog/features.yml`
- `simulation/feature_catalog/scenarios.yml`
- `simulation/feature_catalog/coverage_matrix.yml`
- `tests/feature/test_catalog_integrity.py`
- `reports/coverage/phase0_catalog.json`

Testler:

- Feature ID sayısı 81 olmalı.
- Scenario ID sayısı 83 olmalı.
- Duplicate ID olmamalı.
- Her feature için `simulation_type`, `services`, `positive_replay`, `negative_replay` alanları dolu olmalı.
- Her scenario en az bir feature ile eşleşmeli.

Kapanış komutları:

```bash
pytest tests/feature/test_catalog_integrity.py
python simulation/feature_catalog/validate_catalog.py
```

### Faz 1 — Base LAN, Identity, File, DNS, DHCP, Endpoint

Hedef:

- Kapalı LAN iskeletini kurmak.
- Kimlik, dosya, temel ağ ve endpoint davranışlarını simüle etmek.
- İlk feature test kapısını yeşil yapmak.

Servisler:

- Samba4 AD
- Samba file server
- BIND DNS
- ISC DHCP veya Kea DHCP
- Wazuh manager/agent veya synthetic endpoint log generator
- Zeek veya synthetic network-flow generator
- Filebeat/Logstash/Elasticsearch sadece log doğrulama hattı olarak
- user simulator

Feature kapsamı:

- F-001 SMB/dosya veri çekim profili
- F-002 east-west lateral trafik
- F-003 DNS sorgu entropisi
- F-004 SMB/NTLM downgrade
- F-005 DHCP/ARP anomalisi
- F-006 failed login sonrası success
- F-007 port tarama ve servis keşfi
- F-008 Kerberos/NTLM hacmi
- F-010 servis hesabı interaktif kullanım
- F-011 AD privileged grup değişikliği
- F-015 RDP/PSRemoting hop pattern
- F-037 departman dışı dosya erişimi
- F-038 dosya sunucu toplu okuma/yazma
- F-039 kitlesel dosya rename
- F-040 hassas dizin dolaşma
- F-041 ACL Everyone izin değişikliği
- F-055 USB takma-yazma korelasyonu
- F-057 promiscuous mode
- F-063 bilinmeyen donanım kimliğiyle oturum
- F-079 mesai dışı interaktif oturum
- F-080 boş oturum suistimali
- F-081 rol bazlı aktif çalışma penceresi sapması

Testler:

- Compose config testi.
- Servis health smoke testi.
- DNS/DHCP lease testi.
- AD login success/failure replay testi.
- SMB file access replay testi.
- Port scan replay testi.
- Her listed feature için positive + negative feature test.

Kapanış komutları:

```bash
docker compose config
docker compose up -d
pytest tests/smoke
pytest tests/feature -m phase1
python simulation/feature_catalog/report_coverage.py --phase 1
```

### Faz 2 — Mail, Database, Git, Web, Application Logs

Hedef:

- Mail ve uygulama servislerini kapalı LAN içinde çalıştırmak.
- Mail, DB, Git, HTTP ve uygulama davranışlarını simüle etmek.

Servisler:

- Postfix
- Dovecot
- Roundcube
- PostgreSQL + pg_audit
- Gitea
- Nginx gateway
- internal app mock
- artifact registry mock
- SIEM/admin console mock
- hypervisor console mock

Feature kapsamı:

- F-016 dahili mail gönderim hacmi ve ek boyutu
- F-017 mail forward/delegate kural değişimi
- F-018 mail kutu dışı erişim
- F-019 mail ek entropi ve dosya tipi uyuşmazlığı
- F-020 BCC ve toplu dağıtım sapması
- F-021 kişisel e-posta adreslerine ekli posta
- F-022 bilinmeyen/rakip kuruluşa ekli posta
- F-023 mail içeriğinde hassas anahtar kelime
- F-024 eski mail arşivinin toplu okunması
- F-025 kişi listesi/adres defteri export
- F-026 yazışma üslubu ve dil tonu sapması
- F-027 yasaklı/politika dışı ifade
- F-028 ilk kez harici alıcıya hassas mail
- F-029 kurumsal mail sistemine kişisel hesapla login denemesi
- F-045 veritabanı sorgu hacmi ve tablo kapsamı
- F-046 uygulama süresi ve süreç ağacı
- F-047 iç API çağrı deseni
- F-048 HTTP 4xx yoğunlaşması
- F-049 Git/artifact erişim ve clone hacmi
- F-050 SIEM/log suppress kural değişimi
- F-051 hypervisor ve yönetim konsolu erişimi
- F-052 yeni scheduled task veya servis
- F-053 backup shadow copy silme/devre dışı bırakma
- F-054 kodlanmış veya politika atlatan betikler

Testler:

- Mail send/read/forward replay testleri.
- Postgres bulk select replay testi.
- Gitea mass clone replay testi.
- Nginx 401/403 spike testi.
- Admin console config-change synthetic-log testi.
- Her listed feature için positive + negative feature test.

Kapanış komutları:

```bash
docker compose config
docker compose up -d
pytest tests/integration -m phase2
pytest tests/feature -m phase2
python simulation/feature_catalog/report_coverage.py --phase 2
```

### Faz 3 — AI, Proxy, Physical, HR, Collaboration, Peripheral

Hedef:

- Yeni feature kategorilerindeki AI kullanımı, dış bağlantı, fiziksel erişim, HR lifecycle ve çevre birimi davranışlarını simüle etmek.
- Ağ dışı internet gerektirmeden external-benzeri endpointler mock servislerle taklit edilecek.

Servisler:

- AI gateway mock
- proxy sink
- object storage/cloud mock
- Vault
- Mattermost
- CUPS
- Badge API
- HRIS mock
- SuiteCRM
- wiki/intranet mock
- DLP agent health mock
- keyboard/mouse activity generator

Feature kapsamı:

- F-009 eşzamanlı oturum ve bina içi lokasyon çakışması
- F-012 servis hesabı/API key kullanım haritası
- F-013 secret store okuma burst
- F-014 credential reset/unlock yoğunluğu
- F-030 harici AI platformlarına gizli veri gönderimi
- F-031 kaynak kod/sistem mimarisi AI sohbetine yapıştırma
- F-032 AI prompt içinde iç sistem/kullanıcı/ağ bilgisi
- F-033 onaylanmamış AI araçlarının kullanımı
- F-034 AI platformlarına dosya yükleme
- F-035 AI ile şirket süreçleri/güvenlik prosedürü keşfi
- F-036 AI konuşma geçmişinde strateji/hukuk içeriği
- F-042 yerel diskte hassas veri birikimi
- F-043 etiketli hassas dosyanın kısıtsız alana taşınması
- F-044 wiki/intranet toplu indirme
- F-056 yazıcı iş hacmi ve hassas belge korelasyonu
- F-058 DLP agent sağlık ve bypass denemesi
- F-059 clipboard büyük veri kopyalama
- F-060 ekran görüntüsü alma frekansı
- F-061 rol bazlı sunucu temas haritası
- F-062 iç log arama anahtar kelimesi riski
- F-064 normal aktivite örüntüsünün yoğunlaşması
- F-065 uzun süre kullanılmayan sistemlere ani erişim
- F-066 akran grup davranışından istatistiksel sapma
- F-067 kişisel bulut depolamaya büyük dosya upload
- F-068 ilk kez harici adrese yüksek hacimli transfer
- F-069 proxy üzerinden tünel/alışılmadık protokol
- F-070 badge geçişi ile sistem login uyuşmazlığı
- F-071 composite risk score için çoklu sinyal seti
- F-072 offboarding ayrılan hesap aktivitesi
- F-073 aynı dosya/kayıt çoklu kullanıcı erişim zinciri
- F-074 vardiya dışı fiziksel + mantıksal erişim
- F-075 yeni çalışanın ilk gün aşırı sistem erişimi
- F-076 rol değişikliği sonrası eski yetki kullanımı
- F-077 izin kaydı varken sistem aktivitesi
- F-078 üçüncü taraf/yüklenici kapsam dışı sistem kullanımı

Testler:

- AI gateway prompt/upload replay testleri.
- Proxy/cloud mock upload replay testleri.
- Badge + login correlation replay testleri.
- HRIS offboarding/leave/role-change replay testleri.
- CUPS print replay testi.
- Vault burst replay testi.
- Her listed feature için positive + negative feature test.

Kapanış komutları:

```bash
docker compose config
docker compose up -d
pytest tests/integration -m phase3
pytest tests/feature -m phase3
python simulation/feature_catalog/report_coverage.py --phase 3
```

### Faz 4 — 83 Scenario Replay ve Full Coverage Gate

Hedef:

- 83 senaryo replay edilebilir hale gelsin.
- 81 feature için simülasyon coverage yüzde 100 olsun.
- Full regression raporu üretilsin.

Scenario kapsamı:

- S-001 ile S-083 arası tüm senaryolar.

Testler:

- Her scenario için deterministic replay.
- Her scenario için expected event evidence.
- Her scenario için negative control veya explicit waiver.
- Repeated replay duplicate üretmemeli veya deterministic duplicate key üretmeli.
- Coverage matrix tüm feature ve scenario eşleşmelerini raporlamalı.

Kapanış komutları:

```bash
pytest tests/scenario
pytest tests/feature
python simulation/feature_catalog/report_coverage.py --all
python simulation/scenarios/report_scenario_coverage.py --all
```

---

## 6. Servis Envanteri

Kod yazacak AI, servis eklerken aşağıdaki kurallara uymalıdır:

- Her servis sabit isim kullanır.
- Her servis `corp-lan` ağına bağlıdır.
- Her servis için healthcheck veya smoke kontrolü vardır.
- Her servis için persistent volume veya açıkça stateless gerekçesi vardır.
- Her servis loglarını `logs/` veya log collector path’ine yazar.
- Her servis test fixture’larından bağımsız boot edebilmelidir.

Zorunlu servis grupları:

| Grup | Servisler |
| --- | --- |
| identity | Samba4 AD, LDAP opsiyonel |
| file | Samba file server, audit logs |
| network | BIND DNS, DHCP, Zeek/synthetic-flow, proxy sink |
| endpoint | Wazuh agent veya endpoint synthetic generator |
| mail | Postfix, Dovecot, Roundcube |
| application | PostgreSQL, Gitea, Nginx, internal app mock, wiki/intranet mock |
| security/admin | Vault, SIEM admin mock, hypervisor console mock, DLP health mock |
| physical/hr | Badge API, HRIS mock |
| collaboration | Mattermost, SuiteCRM |
| peripheral | CUPS, USB/clipboard/screenshot synthetic generator |
| validation | Elasticsearch, Logstash, Filebeat veya lightweight log assertion pipeline |

---

## 7. Komut Yüzeyi

Planlanan komutlar:

```bash
make up
make down
make clean
make seed-baseline
make feature FEATURE=F-001
make feature-negative FEATURE=F-001
make scenario SCENARIO=S-001
make test-smoke
make test-integration
make test-features
make test-scenarios
make coverage
make test-all
```

Komutların tamamı `watchtower-demo/server-stack/` altında çalışmalıdır.

---

## 8. Test Stratejisi

Test katmanları:

1. `catalog`: feature/scenario manifest bütünlüğü.
2. `smoke`: container boot, health, port ve volume kontrolleri.
3. `integration`: servisler arası gerçek akış kontrolleri.
4. `feature`: tek feature için positive/negative replay.
5. `scenario`: bir veya daha fazla feature üreten iş akışı replay.
6. `coverage`: feature ve scenario kapsama raporu.

Kabul edilmeyen teslimler:

- Sadece compose yazıp `docker compose config` çalıştırmamak.
- Sadece replay script yazıp test eklememek.
- Sadece positive case yazıp negative control eklememek.
- “Ortam yoktu” deyip gerçek hata çıktısı vermemek.
- Feature coverage raporu üretmemek.

---

## 9. Feature Coverage Gate

Her feature için şu checklist tamamlanmalıdır:

```text
[ ] feature_id manifestte var
[ ] kategori doğru
[ ] faz atanmış
[ ] simülasyon tipi atanmış
[ ] en az bir servis veya synthetic source atanmış
[ ] positive replay komutu var
[ ] negative replay komutu var
[ ] evidence dosyası üretiliyor
[ ] pytest positive assertion var
[ ] pytest negative assertion var
[ ] coverage raporunda PASS görünüyor
```

Faz kapanışında `reports/coverage/feature_coverage.json` şu alanları içermelidir:

```json
{
  "total_features": 81,
  "implemented": 81,
  "positive_tests_passed": 81,
  "negative_tests_passed": 81,
  "waivers": []
}
```

Faz içinde henüz tüm feature’lar bitmediyse `implemented` sadece o faz kapsamını
ifade eder; Faz 4 sonunda `implemented` 81 olmak zorundadır.

---

## 10. Scenario Coverage Gate

Her scenario için şu checklist tamamlanmalıdır:

```text
[ ] scenario_id manifestte var
[ ] ilişkili feature ID listesi var
[ ] kullanılan servisler var
[ ] deterministic seed var
[ ] replay komutu var
[ ] expected event evidence var
[ ] negative control var veya waiver var
[ ] pytest scenario assertion var
[ ] coverage raporunda PASS görünüyor
```

Faz 4 sonunda `reports/coverage/scenario_coverage.json` şu alanları içermelidir:

```json
{
  "total_scenarios": 83,
  "implemented": 83,
  "replay_tests_passed": 83,
  "waivers": []
}
```

---

## 11. Kod Yazacak AI İçin Çalışma Protokolü

Her görev başlangıcında AI şu dosyaları okumalıdır:

- `server-stack/close-server-simulation-implementation-plan.md`
- `server-stack/watchtower-tool-stack.md`
- `server-stack/watchtower-features-final.md`
- `server-stack/watchtower-scenarios-final.md`

Her teslim şu formatta olmalıdır:

```text
YAPILAN İŞ:
- ...

DEĞİŞEN DOSYALAR:
- ...

FEATURE KAPSAMI:
- F-xxx PASS/FAIL

SCENARIO KAPSAMI:
- S-xxx PASS/FAIL

YAZILAN TESTLER:
- ...

ÇALIŞTIRILAN TESTLER:
- komut
- sonuç

RAPORLAR:
- reports/...

KALAN RİSKLER:
- ...
```

`YAZILAN TESTLER` veya `ÇALIŞTIRILAN TESTLER` boşsa teslim geçersizdir.

---

## 12. Prompt Üretim Formatı

Manager AI, implementor AI’a görev verirken bu formatı kullanmalıdır:

```text
[GÖREV]
GÖREV: <tek cümle>
FAZ: <Faz 0|Faz 1|Faz 2|Faz 3|Faz 4>
ROL: <infra|scenario|test>

BAĞLAM:
- Proje: Watchtower closed server simulation
- Kapsam: Sadece server-stack; Watchtower ürün/gözlemleme kodu yok
- Referanslar:
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/close-server-simulation-implementation-plan.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-tool-stack.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-features-final.md
  - /home/caglarkc/Desktop/Github/all-agentics/watchtower-demo/server-stack/watchtower-scenarios-final.md
- Etkilenecek dosyalar: <liste>

YAPILACAK:
1. ...
2. ...

FEATURE KAPSAMI:
- F-...

TESTLER:
1. ...
2. ...

TESLİM KRİTERLERİ:
- değişen dosyalar
- feature coverage
- scenario coverage
- yazılan testler
- çalıştırılan testler
- rapor dosyaları
- kalan riskler
```

---

## 13. Final Acceptance Checklist

Faz 4 sonunda hepsi tamamlanmış olmalıdır:

- [ ] `docker compose config` yeşil.
- [ ] Base LAN servisleri boot ediyor.
- [ ] Identity/file/network servisleri boot ediyor.
- [ ] Mail/DB/Git/Web servisleri boot ediyor.
- [ ] AI/proxy/physical/HR/peripheral mock servisleri boot ediyor.
- [ ] 81 feature manifestte var.
- [ ] 81 feature için simulation path var.
- [ ] 81 feature için positive test var.
- [ ] 81 feature için negative test var veya sıfır waiver hedefi sağlandı.
- [ ] 83 scenario manifestte var.
- [ ] 83 scenario replay ediliyor.
- [ ] Coverage raporları üretiliyor.
- [ ] `make test-all` çalışıyor veya ortam kaynaklı blokaj gerçek hata çıktısıyla belgeleniyor.

---

## 14. Net Sonuç

Bu planın çıktısı bir gözlemleme ürünü değildir.

Bu planın çıktısı:

- kapalı LAN,
- simüle kurumsal servisler,
- deterministic event üretimi,
- feature replay komutları,
- scenario replay komutları,
- positive/negative pytest kanıtları,
- coverage raporlarıdır.

Kod yazacak AI bu dokümanı her fazda self-check listesi olarak kullanmalı ve
testsiz hiçbir fazı tamamlanmış saymamalıdır.
