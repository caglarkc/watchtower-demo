# Watchtower Closed Server Stack

Bu klasor Watchtower urun kodu degildir. `server-stack/`, Watchtower'in 81 feature ve 83 scenario yuzeyini kapali bir sirket aginda test etmek icin kurulan izole simülasyon ortamidir.

Iki ayri test yuzeyi vardir:

- `synthetic`: Deterministic replay YAML, evidence JSON ve coverage gate uzerinden calisan hizli simülasyon.
- `real parity`: Gercek veya real-like kurumsal araclara HTTP/CLI aksiyonlari gonderen, ham log ureten ve kritik yuzeylerde Elasticsearch ingest dogrulayan katman.

Detayli faz gecmisi: [IMPLEMENTATION_HISTORY.md](IMPLEMENTATION_HISTORY.md)

Gercek arac entegrasyon plani: [real-company-tool-integration-plan.md](real-company-tool-integration-plan.md)

## Son Durum

2026-05-23 yerel dogrulama sonucu:

| Gate | Sonuc |
|------|-------|
| `make test-all` | PASS |
| `make test-real-all` | PASS |
| Synthetic feature coverage | 81/81 positive, 81/81 negative |
| Synthetic scenario coverage | 83/83 positive, 83/83 negative |
| Real feature coverage | 81/81 positive, 81/81 negative |
| Real scenario coverage | 83/83 positive, 83/83 negative |
| Real parity | 81/81 L2+, 46/81 L3 |
| Real final gate | PASS, waiver yok |

Raporlar:

- `reports/coverage/feature_coverage.json`
- `reports/coverage/scenario_coverage.json`
- `reports/real/coverage/real_feature_coverage.json`
- `reports/real/coverage/real_scenario_coverage.json`
- `reports/real/coverage/real_final_gate.json`

## Hizli Baslangic

```bash
cd watchtower-demo/server-stack
cp .env.example .env
python3 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
```

Synthetic stack:

```bash
make seed-baseline
make up
make test-all
```

Real parity stack:

```bash
make real-up
make seed-real-all
make test-real-all
```

## En Sik Kullanilan Komutlar

Synthetic feature:

```bash
make feature FEATURE=F-001
make feature-negative FEATURE=F-001
make coverage
```

Synthetic scenario:

```bash
make scenario SCENARIO=S-001
make scenario-negative SCENARIO=S-001
make coverage-scenarios
```

Real feature:

```bash
make real-feature FEATURE=F-001
make real-feature-negative FEATURE=F-001
make real-coverage
```

Real scenario:

```bash
make real-scenario SCENARIO=S-001
make real-scenario-negative SCENARIO=S-001
make real-scenario-coverage
```

Final real gate:

```bash
make test-real-ingest
make real-final-gate
```

## Synthetic Fazlar

| Faz | Kapsam | Gate |
|-----|--------|------|
| Phase 0 | 81 feature manifest, 83 scenario manifest, coverage matrix | `pytest tests/feature/test_catalog_integrity.py` |
| Phase 1 | Base LAN, identity, file, DNS, DHCP, endpoint, network | `pytest tests/feature -m phase1` |
| Phase 2 | Mail, DB, Git, Web/API, admin consoles | `pytest tests/feature -m phase2` |
| Phase 3 | AI, proxy, cloud, secrets, HR, physical, print, collaboration | `pytest tests/feature -m phase3` |
| Phase 4 | 83 scenario replay ve final coverage | `make test-all` |

Synthetic final gate:

```bash
make test-all
```

Beklenen ana ciktilar:

- `tests/smoke`: 4 passed
- `tests/feature`: 337 passed
- `tests/scenario`: 169 passed
- `report_coverage.py --all`: 81/81 PASS
- `report_scenario_coverage.py --all`: 83/83 PASS

## Real Parity Fazlari

| Faz | Kapsam | Parity | Gate |
|-----|--------|--------|------|
| RI-0 | Real metadata, seed dizinleri, real komut yuzeyi | L0 foundation | `pytest tests/real/test_real_catalog.py` |
| RI-1 | Identity, file, DNS, DHCP, network | P0 L3 | `pytest tests/real/features -m p0` |
| RI-2 | Mail, DB, Git, Web/API | P1 L3 | `pytest tests/real/features -m p1` |
| RI-3 | Secrets, AI, proxy, cloud, endpoint behavior | P2 L2 | `pytest tests/real/features -m p2` |
| RI-4 | Physical, HR, collaboration, print, CRM | P3 L2 | `pytest tests/real/features -m p3` |
| RI-5 | 83 scenario real orchestration | L2+ | `pytest tests/real/scenario` |
| RI-6 | Log pipeline ve final ingest gate | 46 L3, 81 L2+ | `make real-final-gate` |

Real final gate:

```bash
make test-real-all
```

Beklenen ana ciktilar:

- `tests/real`: 370 passed
- `tests/real/features -m p0`: 44 passed
- `tests/real/features -m p1`: 48 passed
- `tests/real/features -m p2`: 46 passed
- `tests/real/features -m p3`: 24 passed
- `tests/real/scenario`: 168 passed
- `tests/real/test_real_ingest.py tests/real/test_z_real_final_gate.py`: 5 passed
- `real_feature_coverage.json`: metadata=81/81, ri1=22/22, ri2=24/24, ri3=23/23, ri4=12/12, l3=46/40
- `real_scenario_coverage.json`: pos=83/83, neg=83/83
- `real_final_gate.json`: result=PASS

## Servisler

Ana ag: `corp-lan` (`172.28.0.0/24`).

| Grup | Servisler |
|------|-----------|
| Base LAN | `samba-ad`, `samba-files`, `bind-dns`, `dhcp-server`, `zeek-synthetic`, `endpoint-synthetic`, `log-pipeline`, `elasticsearch` |
| Mail/App | `postfix`, `dovecot`, `roundcube`, `postgres`, `gitea`, `nginx`, `internal-app`, `artifact-registry`, `siem-admin`, `hypervisor-console` |
| Security/AI | `ai-gateway-mock`, `proxy-sink`, `cloud-storage-mock`, `vault-mock`, `dlp-mock`, `activity-generator` |
| HR/Physical/Collab | `badge-api`, `hris-mock`, `mattermost`, `cups`, `suitecrm-mock`, `wiki-mock` |
| Real action helpers | `samba-files-actions`, `dhcp-logger`, `postgres-actions`, `gitea-actions` |

Health kontrolu:

```bash
docker compose ps
make test-smoke
```

Not: Smoke test artik sadece container adini degil, container `State=running` ve varsa `Health=healthy` durumunu da kontrol eder.

## Evidence ve Log Dizini

Synthetic evidence:

- `reports/features/F-xxx-positive.json`
- `reports/features/F-xxx-negative.json`
- `reports/scenarios/S-xxx-positive.json`
- `reports/scenarios/S-xxx-negative.json`

Real evidence:

- `reports/real/features/F-xxx-positive.json`
- `reports/real/features/F-xxx-negative.json`
- `reports/real/scenarios/S-xxx-positive.json`
- `reports/real/scenarios/S-xxx-negative.json`

Ham loglar:

- `logs/identity/ad_events.jsonl`
- `logs/samba/audit.log`
- `logs/dhcp/dhcpd.log`
- `logs/zeek/conn.log`
- `logs/postfix/postfix.jsonl`
- `logs/postgres/pg_audit.log`
- `logs/gitea/gitea-access.jsonl`
- `logs/nginx/access.log`
- `logs/vault/audit.jsonl`
- `logs/proxy/proxy_sink.jsonl`
- `logs/ai_gateway/ai_gateway.jsonl`
- `logs/hris/hris.jsonl`
- `logs/badge/badge.jsonl`

## Dogrulama Sirasinda Yapilan Duzeltmeler

Son kontrol sirasinda uc tutarsizlik bulundu ve duzeltildi:

- `bind-dns` query logging konfigurasyonu host mount izinleri nedeniyle container restart'a dusuruyordu. BIND config tarafindaki yazma zorunlulugu kaldirildi; DNS real testi host fallback log yolunu da kabul ediyor.
- RI-1/RI-2 metadata testleri halen `L2` bekliyordu, fakat RI-6 ile P0/P1 feature'lari `L3` seviyesine yukseltilmisti. Testler `L2 veya ustu` olacak sekilde guncellendi.
- Smoke test container adlarini gormeyi yeterli sayiyordu. Artik servislerin calisir ve healthy olmasi zorunlu.

Bu duzeltmelerden sonra calistirilan hedef regresyon:

```bash
.venv/bin/pytest tests/real/test_identity_file_network.py tests/real/test_mail_db_git_web.py tests/smoke -q
```

Sonuc: `16 passed`.

## Sinirlar

Bu ortam production kopyasi degildir; kapali LAN icin test edilebilir real-like lab ortamidir.

- Mail servisleri tam MTA/IMAP davranisi yerine action API ve audit log uretir.
- `vault-mock`, `ai-gateway-mock`, `hris-mock`, `suitecrm-mock`, `dlp-mock` real-like servislerdir.
- L3 ingest, logun Elasticsearch indeksine yazildigini dogrular; Wazuh kural semantigini birebir garanti etmez.
- Watchtower urun kodu bu klasorde calistirilmaz; bu stack Watchtower'in gozlemleyecegi kapali sirket ortamini saglar.
