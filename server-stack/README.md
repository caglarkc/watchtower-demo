# Watchtower Closed Server Stack

Kapalı `corp-lan` simülasyon ortamı (Phase 1: kimlik, dosya, DNS, DHCP, endpoint, ağ akışı).

## Gerçek araç entegrasyon planı

Mevcut stack 81 feature ve 83 scenario için deterministic simülasyon coverage sağlar.
Gerçek kurumsal araç paritesine geçiş planı:

- [real-company-tool-integration-plan.md](real-company-tool-integration-plan.md)

Bu ek plan mock/synthetic kaynakları kademeli olarak Samba4 AD, Samba audit,
BIND query log, DHCP/Kea, Zeek, Wazuh/auditd, Postfix/Dovecot/Roundcube,
PostgreSQL pg_audit, Gitea, Nginx, Vault, Squid/MinIO, CUPS, HRIS/Badge
real-like servisleri ve gerçek protokol replay testleriyle değiştirmeyi hedefler.

### RI-0 — Real parity foundation

Synthetic `make test-all` davranışı değişmez. Real katman ayrı komutlardadır:

```bash
make real-up
make seed-real-all
make real-feature FEATURE=F-001
make real-feature-negative FEATURE=F-001
pytest tests/real/test_real_catalog.py
make real-coverage
make test-real-all
```

Kanıt: `reports/real/features/F-xxx-{positive,negative}.json`, coverage: `reports/real/coverage/real_feature_coverage.json`

## Hızlı başlangıç

```bash
cp .env.example .env
python3 -m venv .venv && .venv/bin/pip install -r requirements-test.txt
make seed-baseline
make config
make up
make test-smoke
make test-phase1
make coverage
```

## Feature replay

```bash
make feature FEATURE=F-001
make feature-negative FEATURE=F-001
# Kanıt: reports/features/F-001.json
```

## Servisler (corp-lan 172.28.0.0/24)

| Servis | IP | Rol |
|--------|-----|-----|
| samba-ad | .10 | AD kimlik log simülatörü |
| samba-files | .11 | SMB dosya sunucusu |
| bind-dns | .12 | BIND9 DNS |
| dhcp-server | .13 | ISC DHCP |
| zeek-synthetic | .14 | Zeek conn.log üretici |
| endpoint-synthetic | .15 | Endpoint/AD/USB olay API |
| log-pipeline | .16 | Log assertion hattı |
| elasticsearch | .17 | Log doğrulama (ES) |

Tam Samba4 DC için: `docker compose --profile real-ad up -d`

## Phase 1 feature’lar (22)

F-001, F-002, F-003, F-004, F-005, F-006, F-007, F-008, F-010, F-011, F-015, F-037, F-038, F-039, F-040, F-041, F-055, F-057, F-063, F-079, F-080, F-081

## Phase 2 — Mail, DB, Git, Web

```bash
make seed-phase2
make up
make test-integration
make test-phase2
make coverage-phase2
```

### Phase 2 servisler (172.28.0.20–29)

| Servis | IP | Rol |
|--------|-----|-----|
| postfix | .20 | SMTP log sim |
| dovecot | .21 | IMAP log sim |
| roundcube | .22 | Webmail log sim |
| postgres | .23 | PostgreSQL + init schema |
| gitea | .24 | Git sunucusu |
| nginx | .25 | API gateway |
| internal-app | .26 | İç uygulama mock |
| artifact-registry | .27 | Artifact mock |
| siem-admin | .28 | SIEM admin mock |
| hypervisor-console | .29 | Hypervisor mock |

### Phase 2 feature’lar (24)

F-016..F-029 (mail), F-045..F-054 (uygulama/DB/Git/HTTP/admin/endpoint)

## Phase 3 — AI, Proxy, Physical, HR, Collaboration

```bash
make seed-phase3
make up
make test-integration-phase3
make test-phase3
make coverage-phase3
```

### Phase 3 servisler (172.28.0.30–41)

| Servis | IP |
|--------|-----|
| ai-gateway-mock | .30 |
| proxy-sink | .31 |
| cloud-storage-mock | .32 |
| vault-mock | .33 |
| mattermost | .34 |
| cups | .35 |
| badge-api | .36 |
| hris-mock | .37 |
| suitecrm-mock | .38 |
| wiki-mock | .39 |
| dlp-mock | .40 |
| activity-generator | .41 |

### Phase 3 feature’lar (35)

F-009, F-012–F-014, F-030–F-036, F-042–F-044, F-056, F-058, F-059–F-062, F-064–F-071, F-072–F-078
