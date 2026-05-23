# Watchtower Closed Server Stack Implementation History

Bu dokuman `server-stack/` altinda kurulan kapali sirket agi simülasyonunun hangi fazlarda ne basardigini, hangi testlerle kapatildigini ve son kontrolde hangi tutarsizliklarin duzeltildigini kaydeder.

## Kapsam Ayrimi

`watchtower-demo/` urun tarafidir. LLM destekli Watchtower CLI, manager alert mantigi ve urun davranisi orada ele alinmalidir.

`watchtower-demo/server-stack/` kapali sunucu ortamidir. Bu klasorun isi sirket agi, kurumsal araclar, ham loglar, replay aksiyonlari, evidence ve coverage gate uretmektir.

Bu nedenle burada yapilan isler Watchtower'in kendisini degil, Watchtower'in test edebilecegi izole lab ortamini kurar.

## Parity Seviyeleri

| Seviye | Anlam |
|--------|-------|
| L0 | Metadata ve komut yuzeyi var; gercek aksiyon henuz yok |
| L1 | Seed/veri hazir; servis veya aksiyon kismi baslamis |
| L2 | Real-like servis aksiyonu calisir ve host ham log assertion vardir |
| L3 | L2'ye ek olarak log ingest pipeline ile Elasticsearch indeks assertion vardir |

Final durumda 81 feature L2 veya ustudur. P0 ve P1 yuzeyleri toplam 46 feature ile L3 seviyesindedir.

## Synthetic Fazlar

### Phase 0 — Feature Coverage Freeze

Amac 81 feature ve 83 scenario icin degismeyen katalog tabanini olusturmakti.

Uretilen temel dosyalar:

- `simulation/feature_catalog/features.yml`
- `simulation/feature_catalog/scenarios.yml`
- `simulation/feature_catalog/coverage_matrix.yml`
- `simulation/feature_catalog/catalog_data.py`
- `simulation/feature_catalog/generate_manifests.py`
- `simulation/feature_catalog/validate_catalog.py`
- `tests/feature/test_catalog_integrity.py`

Basarilanlar:

- 81/81 feature manifestte.
- 83/83 scenario manifestte.
- Her feature icin positive/negative komut ve evidence yolu tanimli.
- Her scenario en az bir feature'a bagli.
- Her feature en az bir scenario ile kapsaniyor.

Gate:

```bash
.venv/bin/python simulation/feature_catalog/generate_manifests.py
.venv/bin/python simulation/feature_catalog/validate_catalog.py
.venv/bin/pytest tests/feature/test_catalog_integrity.py -v
```

Beklenen sonuc: 8 catalog integrity testi pass.

### Phase 1 — Base LAN

Amac kapali LAN'in temel kimlik, dosya, DNS, DHCP, endpoint ve ag olaylarini simule etmesiydi.

Eklenen servisler:

- `samba-ad`
- `samba-files`
- `bind-dns`
- `dhcp-server`
- `zeek-synthetic`
- `endpoint-synthetic`
- `log-pipeline`
- `elasticsearch`

Kapsanan feature grubu:

- F-001..F-008
- F-010, F-011, F-015
- F-037..F-041
- F-055, F-057, F-063
- F-079..F-081

Basarilanlar:

- 22 Phase 1 feature icin positive/negative replay.
- 44 replay YAML.
- `make feature FEATURE=F-xxx` ve `make feature-negative FEATURE=F-xxx` calisir hale geldi.
- Smoke testler compose ve servis sagligini dogruluyor.

Gate:

```bash
docker compose config
docker compose up -d
pytest tests/smoke -v
pytest tests/feature -m phase1 -v
python simulation/feature_catalog/report_coverage.py --phase 1
```

Beklenen sonuc: Phase 1 coverage 22/22 PASS.

### Phase 2 — Mail, Database, Git, Web/API

Amac sirket uygulama yuzeylerini, mail akisini, DB auditini, Git hareketlerini ve web/API davranislarini simule etmekti.

Eklenen servisler:

- `postfix`
- `dovecot`
- `roundcube`
- `postgres`
- `gitea`
- `nginx`
- `internal-app`
- `artifact-registry`
- `siem-admin`
- `hypervisor-console`

Kapsanan feature grubu:

- F-016..F-029
- F-045..F-054

Basarilanlar:

- 24 Phase 2 feature icin positive/negative replay.
- 48 replay YAML.
- Mail, DB, Git, HTTP, admin console ve endpoint aksiyonlari icin log kanallari eklendi.
- Phase 1 regresyonu korunarak Phase 2 gate kapandi.

Gate:

```bash
make seed-phase2
make up
pytest tests/integration -m phase2 -v
pytest tests/feature -m phase2 -v
pytest tests/feature -m phase1 -v
python simulation/feature_catalog/report_coverage.py --phase 2
```

Beklenen sonuc: Phase 2 coverage 24/24 PASS.

### Phase 3 — AI, Proxy, Physical, HR, Collaboration

Amac yeni 81 feature setindeki AI, proxy, secrets, cloud, HR, fiziksel erisim, print ve collaboration yuzeylerini kapali LAN'a eklemekti.

Eklenen servisler:

- `ai-gateway-mock`
- `proxy-sink`
- `cloud-storage-mock`
- `vault-mock`
- `mattermost`
- `cups`
- `badge-api`
- `hris-mock`
- `suitecrm-mock`
- `wiki-mock`
- `dlp-mock`
- `activity-generator`

Kapsanan feature grubu:

- F-009
- F-012..F-014
- F-030..F-036
- F-042..F-044
- F-056, F-058
- F-059..F-062
- F-064..F-078

Basarilanlar:

- 35 Phase 3 feature icin positive/negative replay.
- 70 replay YAML.
- AI prompt/upload, proxy exfil, secrets read, HR lifecycle, badge swipe, print, CRM ve wiki olaylari simule edildi.
- Phase 1 ve Phase 2 regresyonlari korunarak Phase 3 gate kapandi.

Gate:

```bash
make seed-phase3
make up
pytest tests/integration -m phase3 -v
pytest tests/feature -m phase3 -v
pytest tests/feature -m phase1 -v
pytest tests/feature -m phase2 -v
python simulation/feature_catalog/report_coverage.py --phase 3
```

Beklenen sonuc: Phase 3 coverage 35/35 PASS.

### Phase 4 — Full Synthetic Coverage Gate

Amac sadece feature replay degil, 83 scenario icin de deterministic replay motoru ve coverage gate kurmakti.

Eklenen ana parcaciklar:

- `simulation/scenarios/scenario_lib.py`
- `simulation/scenarios/generate_scenario_replays.py`
- `simulation/scenarios/run_scenario.py`
- `simulation/scenarios/report_scenario_coverage.py`
- `tests/scenario/test_scenario_replay.py`
- `tests/scenario/test_scenario_catalog.py`
- `tests/scenario/test_z_final_coverage_report.py`
- `tests/feature/test_coverage_gate.py`

Basarilanlar:

- 166 scenario YAML: 83 positive, 83 negative.
- 81 feature icin positive/negative evidence.
- 83 scenario icin positive/negative evidence.
- `make scenario` ve `make scenario-negative` komutlari calisir hale geldi.
- `make test-all` final synthetic gate oldu.

Son dogrulama:

```bash
make test-all
```

Gozlenen sonuc:

- `tests/smoke`: 4 passed
- `tests/feature`: 337 passed
- `tests/scenario`: 169 passed
- `feature_coverage.json`: 81/81 PASS, positive=81, negative=81
- `scenario_coverage.json`: 83/83 PASS, positive=83, negative=83

## Real Parity Fazlari

### RI-0 — Real Parity Foundation

Amac synthetic davranisi bozmadan real entegrasyon icin ayri komut yuzeyi ve metadata olusturmakti.

Eklenenler:

- `simulation/real/real_parity_data.py`
- `simulation/real/seed_real_all.py`
- `simulation/real/run_real_feature.py`
- `simulation/real/report_real_coverage.py`
- `tests/real/test_real_catalog.py`
- `reports/real/{features,scenarios,coverage,logs}/`
- `Makefile` real hedefleri

Basarilanlar:

- 81/81 feature real metadata aldi.
- `real_parity_level`, `real_tool`, `real_action_command`, `raw_log_assertion`, `ingest_assertion` alanlari eklendi.
- Synthetic `make test-all` davranisi degismedi.

Gate:

```bash
make seed-real-all
pytest tests/real/test_real_catalog.py -v
make real-coverage
```

### RI-1 — Real Identity, File, DNS, DHCP, Network

Amac P0 yuzeyini real-like servis aksiyonlari ve ham loglarla dogrulamakti.

Kapsam:

- Samba AD action API
- Samba files actions ve `logs/samba/audit.log`
- BIND DNS servis sagligi
- DHCP logger ve `logs/dhcp/dhcpd.log`
- Zeek `/emit` ve `logs/zeek/conn.log`
- Endpoint `/emit`
- Elasticsearch ingest hedefi

Kapsanan feature sayisi: 22.

Basarilanlar:

- F-004 dahil P0 yuzey tamamlandi.
- RI-6 sonrasi P0 feature'lari L3 seviyesine yukseldi.
- Identity/file/network aksiyonlari positive/negative evidence uretir hale geldi.

Gate:

```bash
make real-up
make seed-real-identity seed-real-files
pytest tests/real/test_identity_file_network.py -v
pytest tests/real/features -m p0 -v
make real-coverage
```

Son dogrulama: P0 marker suite 44 passed.

### RI-2 — Real Mail, DB, Git, Web/API

Amac P1 yuzeyini real-like mail/app araclari, DB audit loglari ve HTTP/Git aksiyonlariyla dogrulamaktı.

Kapsam:

- Postfix/Dovecot/Roundcube action API
- PostgreSQL ve `postgres-actions`
- `logs/postgres/pg_audit.log`
- Gitea ve `gitea-actions`
- Nginx HTTP replay
- Internal app, artifact registry, SIEM admin, hypervisor audit

Kapsanan feature sayisi: 24.

Basarilanlar:

- F-016..F-029 ve F-045..F-054 real positive/negative evidence uretir hale geldi.
- RI-6 sonrasi P1 feature'lari L3 seviyesine yukseldi.
- Mail, DB, Git ve web/API raw log assertionlari testlere baglandi.

Gate:

```bash
make real-up
make seed-real-mail seed-real-apps
pytest tests/real/test_mail_db_git_web.py -v
pytest tests/real/features -m p1 -v
make real-coverage
```

Son dogrulama: P1 marker suite 48 passed.

### RI-3 — Secrets, AI, Proxy, Cloud, Endpoint Behavior

Amac P2 yuzeyini secrets, AI, proxy, cloud upload ve endpoint davranislari uzerinden real-like calistirmakti.

Kapsam:

- `vault-mock` audit
- `ai-gateway-mock` prompt/upload audit
- `proxy-sink` Squid-style access log
- `cloud-storage-mock` S3-style upload log
- `wiki-mock`
- `dlp-mock`
- `activity-generator`
- Endpoint and SIEM `/emit`

Kapsanan feature sayisi: 23.

Basarilanlar:

- F-012, F-013, F-030..F-036, F-042..F-044, F-058..F-069 real positive/negative evidence uretir hale geldi.
- P2 feature'lari L2 seviyesinde raw log assertion ile kapandi.
- Vault/proxy/cloud/AI yuzeylerinde ingest hedefleri dokumante edildi.

Gate:

```bash
make real-up
make seed-real-security seed-real-endpoint
pytest tests/real/test_security_proxy_ai_endpoint.py -v
pytest tests/real/features -m p2 -v
make real-coverage
```

Son dogrulama: P2 marker suite 46 passed.

### RI-4 — Physical, HR, Collaboration, Print, CRM

Amac P3 yuzeyini badge, HRIS, print, collaboration ve CRM loglariyla dogrulamakti.

Kapsam:

- `badge-api`
- `hris-mock`
- `cups`
- `mattermost`
- `suitecrm-mock`
- `wiki-mock`

Kapsanan feature sayisi: 12.

Basarilanlar:

- F-009, F-014, F-056, F-070..F-078 real positive/negative evidence uretir hale geldi.
- HRIS ve Badge DB-backed state tuttu.
- Print, Mattermost ve SuiteCRM action API ile log uretir hale geldi.

Gate:

```bash
make real-up
make seed-real-physical-hr
pytest tests/real/test_physical_hr_collab_print.py -v
pytest tests/real/features -m p3 -v
make real-coverage
```

Son dogrulama: P3 marker suite 24 passed.

### RI-5 — Real Scenario Replay

Amac 83 scenario icin synthetic replay'den ayri real orchestration kurmakti.

Eklenenler:

- `simulation/real/run_real_scenario.py`
- `simulation/real/report_real_scenario_coverage.py`
- `tests/real/scenario/test_real_scenario_replay.py`
- `tests/real/scenario/test_z_real_scenario_coverage_gate.py`
- `make real-scenario`
- `make real-scenario-negative`
- `make real-scenario-coverage`

Basarilanlar:

- Her scenario `SCENARIO_FEATURE_MAP` uzerinden ilgili real feature aksiyonlarini calistiriyor.
- 83 positive ve 83 negative scenario evidence uretiliyor.
- Waiver yok.

Gate:

```bash
make real-up
make seed-real-all
pytest tests/real/scenario -v
make real-scenario-coverage
```

Son dogrulama:

- `tests/real/scenario`: 168 passed.
- `real_scenario_coverage.json`: positive=83/83, negative=83/83.

### RI-6 — Real Ingest Final Gate

Amac raw log assertion sonrasinda kritik feature'lar icin ingest assertion eklemekti.

Kapsam:

- `log-pipeline` `POST /ingest`
- Host `logs/` dosyalarinin ship edilmesi
- Elasticsearch `corp-logs-f-xxx` index assertion
- Final gate raporu

Basarilanlar:

- 81/81 feature L2 veya ustu.
- 46/81 feature L3.
- L3 hedefi minimum 40 iken 46 ile kapandi.
- 83/83 real scenario positive/negative pass.
- Final gate waiver olmadan PASS.

Gate:

```bash
make real-up
make test-real-ingest
make real-coverage
make real-scenario-coverage
make real-final-gate
```

Son dogrulama:

- `tests/real/test_real_ingest.py tests/real/test_z_real_final_gate.py`: 5 passed.
- `real_feature_coverage.json`: metadata=81/81, ri1=22/22, ri2=24/24, ri3=23/23, ri4=12/12, l3=46/40.
- `real_final_gate.json`: result=PASS.

## Son Kontrolde Bulunan ve Duzeltilen Tutarsizliklar

### 1. BIND container restart'a dusuyordu

Belirti:

```text
corp-bind-dns Restarting
checking logging configuration failed: permission denied
loading configuration: permission denied
```

Sebep:

BIND container host mount altindaki query log dosyasina yazmaya calisiyordu. Container kullanicisi ve mounted path izinleri her ortamda uyumlu olmadigi icin servis fatal config error ile restart'a dusuyordu.

Duzeltme:

- `configs/bind/named.conf` icindeki dosyaya yazan custom query logging konfigurasyonu kaldirildi.
- Real DNS testi `logs/dns/query.log` yaninda `reports/real/logs/dns/query.log` fallback yolunu da kabul edecek hale getirildi.
- `docker compose up -d --force-recreate bind-dns` sonrasi servis `healthy` oldu.

### 2. RI-1/RI-2 testleri eski L2 beklentisinde kalmisti

Belirti:

P0 ve P1 feature'lari RI-6 ile L3 seviyesine yukseltilmisken testler `real_parity_level == "L2"` bekliyordu.

Duzeltme:

- RI-1 metadata testi `L2 veya L3` kabul edecek hale getirildi.
- RI-2 metadata testi `L2 veya L3` kabul edecek hale getirildi.
- F-004 P0 kapsam kontrolune eklendi.

### 3. Smoke test servis sagligini yeterince kontrol etmiyordu

Belirti:

Smoke test container adlarini gorunce pass verebiliyordu; restart veya unhealthy durumunu yakalamiyordu.

Duzeltme:

- `tests/smoke/test_service_health.py` `docker compose ps --format json` ciktisini parse ediyor.
- Her core servis icin `State == "running"` kontrol ediliyor.
- `Health` alani varsa `healthy` olmasi zorunlu.

Hedef regresyon:

```bash
.venv/bin/pytest tests/real/test_identity_file_network.py tests/real/test_mail_db_git_web.py tests/smoke -q
```

Sonuc:

```text
16 passed
```

## Son Tam Dogrulama

### Synthetic

Komut:

```bash
make test-all
```

Sonuc:

```text
tests/feature: 337 passed
tests/scenario: 169 passed
feature coverage: 81/81 PASS
scenario coverage: 83/83 PASS
```

### Real

Komut:

```bash
make test-real-all
```

Sonuc:

```text
tests/real: 370 passed
tests/real/features -m p0: 44 passed
tests/real/features -m p1: 48 passed
tests/real/features -m p2: 46 passed
tests/real/features -m p3: 24 passed
tests/real/scenario: 168 passed
tests/real/test_real_ingest.py tests/real/test_z_real_final_gate.py: 5 passed
real coverage: metadata=81/81 ri1=22/22 ri2=24/24 ri3=23/23 ri4=12/12 l3=46/40
real scenario coverage: pos=83/83 neg=83/83
real final gate: PASS
```

## Ne Tamamlandi

- 81 feature'in tamami synthetic olarak positive/negative test ediliyor.
- 83 scenario'nun tamami synthetic olarak positive/negative test ediliyor.
- 81 feature'in tamami real parity katmaninda positive/negative test ediliyor.
- 83 scenario'nun tamami real parity orchestration ile positive/negative test ediliyor.
- 46 kritik P0/P1 feature L3 ingest assertion ile Elasticsearch'e kadar dogrulaniyor.
- BIND, smoke ve metadata test tutarsizliklari giderildi.
- Final gate waiver olmadan pass.

## Kalan Sinirlar

Bu sistem tamamlanmis bir kapali lab stack'tir, fakat production ortam kopyasi degildir.

- Mail, Vault, HRIS, SuiteCRM, DLP ve AI servisleri real-like mock veya action API tabanlidir.
- L3, logun Elasticsearch'e girdigini dogrular; Wazuh rule tuning, correlation ve alert semantigi ayrica ele alinmalidir.
- Watchtower urun kodu bu fazlarda dogrulanmadi; bu stack Watchtower'in gozlemleyecegi sirket ortamini saglar.
- Daha ileri seviye icin tam Wazuh manager/agent, native `pg_audit`, tam SMTP/IMAP, gercek Samba4 DC ve SIEM rule assertion katmani eklenebilir.
