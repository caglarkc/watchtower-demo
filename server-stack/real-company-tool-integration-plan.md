# Real Company Tool Integration Plan

> [!IMPORTANT]
> Bu plan `server-stack` icindir. Watchtower urun kodu, CLI, alert engine,
> LLM veya manager notification bu planin kapsami degildir.
>
> Hedef: Mevcut 81/81 feature + 83/83 scenario synthetic coverage'i koruyarak
> kapali LAN icinde gercek kurumsal araclarla, ham seed data ile ve gercek
> protokol aksiyonlariyla test edilebilir hale getirmek.

---

## 1. Hedef Seviye

Mevcut durum:

- 81 feature icin positive/negative replay var.
- 83 scenario icin positive/negative replay var.
- Servislerin bir kismi gercek container, buyuk kismi deterministic mock veya synthetic log generator.

Hedef durum:

- Her feature en az `L2` seviyesine cikar.
- Kritik altyapi feature'lari `L3` seviyesine cikar.
- Ham kurumsal data seed'leri vardir.
- Replay scriptleri gercek servis/protokol aksiyonu calistirir.
- Testler sadece evidence JSON'a degil, gercek servis loguna veya ingest index'ine bakar.

Parite seviyeleri:

| Seviye | Anlam | Kabul kosulu |
| --- | --- | --- |
| L0 synthetic | Sadece fixture/evidence JSON | Mevcut durum, yeni hedef icin yeterli degil |
| L1 service-log | Gercek veya real-like servis boot eder ve log yazar | Health + log assertion |
| L2 real-action | Replay gercek protokol/API/CLI aksiyonu yapar | Aksiyon + servis log assertion |
| L3 ingested | Event log pipeline'dan Elasticsearch/Wazuh index'e akar | L2 + index/query assertion |

Final hedef:

```json
{
  "total_features": 81,
  "l2_or_higher": 81,
  "l3_core_features": 40,
  "positive_real_tests_passed": 81,
  "negative_real_tests_passed": 81,
  "waivers": []
}
```

---

## 2. Gercek Arac Stack'i

Mevcut mock/synthetic stack korunur. Gercek araclar Docker Compose profile'lariyla
eklenir.

Profile isimleri:

- `real-identity`
- `real-network`
- `real-mail`
- `real-apps`
- `real-security`
- `real-physical-hr`
- `real-endpoint`
- `real-ingest`
- `real-all`

Arac eslesmeleri:

| Alan | Gercek / real-like arac | Not |
| --- | --- | --- |
| AD / LDAP | Samba4 AD DC + OpenLDAP fallback | Windows DC yerine kapali LAN uyumlu Samba4 |
| File server | Samba SMB + full_audit VFS | Dosya access/rename/ACL loglari |
| DNS | BIND9 query logging | DNS entropy/tunnel tests |
| DHCP | Kea DHCP veya ISC DHCP + lease logs | DHCP/rogue scenario |
| Network visibility | Zeek + traffic-generator containers | Gercek conn/dns/http logs |
| Endpoint security | Wazuh manager + Linux Wazuh agents + auditd | Windows Event ID synthetic bridge gerekebilir |
| Mail | docker-mailserver veya Postfix+Dovecot+Roundcube | SMTP/IMAP/forward/archive logs |
| DB | PostgreSQL + pg_audit | Gercek SELECT/DDL audit |
| Git | Gitea + real repos | Gercek clone/fetch/http logs |
| Web/API | Nginx + internal app | HTTP 4xx/API pattern |
| Secrets | Vault OSS dev server + file audit | Secret burst/API key tests |
| Proxy / egress | Squid proxy + MinIO/S3 mock + external-domain sink | Cloud/external/tunnel tests |
| AI gateway | Open WebUI veya minimal audited AI gateway | Internet yok; local audit endpoint |
| Collaboration | Mattermost | Chat/credential-pattern logs |
| Print | CUPS | Print job logs |
| CRM | SuiteCRM veya lightweight CRM app | CRM export/access |
| HRIS | real-like internal HRIS app with DB + audit | Offboarding/leave/role-change |
| Badge | real-like Badge API + DB + audit | Physical/logical correlation |
| DLP | real-like DLP health agent | Health/bypass logs |
| Hypervisor | Cockpit/libvirt mockable audit or real-like console app | Management access logs |
| SIEM admin | Wazuh/Elastic rule config audit or real-like SIEM admin app | Suppress rule changes |

Mock kalmasi kabul edilebilir tek alanlar:

- Fiziksel badge donanimi yerine real-like Badge API.
- HRIS SaaS yerine real-like HRIS app.
- DLP vendor agent yerine real-like DLP health service.
- Windows workstation yerine Linux endpoint + Windows Event bridge fixture.

Bu alanlarda bile L2 hedefi gecerlidir: replay gercek HTTP/API/CLI aksiyonu yapmali,
log sadece elle yazilmamalidir.

---

## 3. Ham Data Seed Gereksinimi

Tum seed data `server-stack/seeds/real/` altinda tutulur.

Zorunlu seed setleri:

```text
seeds/real/
├── identity/
│   ├── users.csv
│   ├── groups.csv
│   ├── service_accounts.csv
│   ├── contractors.csv
│   └── org_units.ldif
├── files/
│   ├── finance/
│   ├── hr/
│   ├── legal/
│   ├── dev/
│   ├── public/
│   └── classification.yml
├── mail/
│   ├── mailboxes.yml
│   ├── distribution_lists.yml
│   ├── forwarding_rules.yml
│   └── attachments/
├── postgres/
│   ├── schema.sql
│   ├── pii_customers.csv
│   ├── payroll.csv
│   └── audit_seed.sql
├── git/
│   ├── repos.yml
│   └── repo_templates/
├── web/
│   ├── api_users.yml
│   ├── endpoints.yml
│   └── access_patterns.yml
├── vault/
│   ├── policies.hcl
│   ├── secrets.yml
│   └── tokens.yml
├── hris/
│   ├── employees.csv
│   ├── leave_calendar.csv
│   ├── offboarding.csv
│   └── role_changes.csv
├── badge/
│   ├── locations.yml
│   └── badge_events.csv
├── ai/
│   ├── prompts.yml
│   ├── uploads/
│   └── blocked_domains.yml
└── baseline/
    ├── normal_day.yml
    ├── peer_groups.yml
    └── work_windows.yml
```

Seed kurallari:

- Gercek PII yok; tum data synthetic ama kurumsal sekilde gercekci.
- Kullanici, departman, host, IP, badge ve HR kayitlari birbiriyle tutarli.
- Her feature en az bir positive ve bir negative seed path'e baglanir.
- Tum seed komutlari idempotent olmalidir.

---

## 4. Komut Yuzeyi

Yeni real integration komutlari:

```bash
make real-config
make real-up
make real-down
make real-clean

make seed-real-all
make seed-real-identity
make seed-real-files
make seed-real-mail
make seed-real-apps
make seed-real-security
make seed-real-physical-hr
make seed-real-endpoint

make real-feature FEATURE=F-001
make real-feature-negative FEATURE=F-001
make real-scenario SCENARIO=S-001
make real-scenario-negative SCENARIO=S-001

make test-real-smoke
make test-real-ingest
make test-real-features
make test-real-scenarios
make real-coverage
make test-real-all
```

Evidence dosyalari:

```text
reports/real/features/F-001-positive.json
reports/real/features/F-001-negative.json
reports/real/scenarios/S-001-positive.json
reports/real/scenarios/S-001-negative.json
reports/real/coverage/real_feature_coverage.json
reports/real/coverage/real_scenario_coverage.json
```

Her real evidence su alanlari icermelidir:

```json
{
  "id": "F-001",
  "mode": "positive",
  "parity_level": "L2",
  "actions_executed": [],
  "raw_logs_asserted": [],
  "ingest_assertions": [],
  "seed_refs": [],
  "result": "PASS"
}
```

---

## 5. Oncelik Sirasi

Tum feature'lar yapilacak. Sira, guvenlik degeri ve entegrasyon bagimliligina gore
kritikten daha az kritige dogrudur.

### P0 — Core identity, file, network, exfil

Once yapilacak cunku diger bircok scenario bunlara baglanir.

- F-001, F-002, F-003, F-005, F-006, F-007, F-008
- F-010, F-011, F-015
- F-037, F-038, F-039, F-040, F-041
- F-045, F-048, F-049
- F-055, F-057, F-079, F-080, F-081

### P1 — Mail, DB, Git, API, privilege/admin

- F-016, F-017, F-018, F-019, F-020, F-021, F-022, F-023, F-024, F-025, F-026, F-027, F-028, F-029
- F-046, F-047, F-050, F-051, F-052, F-053, F-054

### P2 — Secrets, AI, proxy, cloud, behavioral

- F-012, F-013, F-030, F-031, F-032, F-033, F-034, F-035, F-036
- F-042, F-043, F-044
- F-058, F-059, F-060, F-061, F-062, F-064, F-065, F-066
- F-067, F-068, F-069

### P3 — Physical, HR lifecycle, multi-signal

- F-009, F-014
- F-056
- F-070, F-071, F-072, F-073, F-074
- F-075, F-076, F-077, F-078

---

## 6. 81 Feature Real Integration Matrix

Her feature icin hedef minimum `L2`dir. `L3` isaretli feature'lar ingest/index
assertion da istemelidir.

| Feature | Oncelik | Real tool/action | Raw data | Assertion |
| --- | --- | --- | --- | --- |
| F-001 | P0 | smbclient copy/read from Samba share + Zeek flow | classified files, AD users | Samba audit + Zeek conn, L3 |
| F-002 | P0 | traffic generator connects to many internal hosts/ports | host inventory | Zeek conn fan-out, L3 |
| F-003 | P0 | dig/nslookup high entropy TXT/NXDOMAIN queries | DNS zone + query list | BIND query log, L3 |
| F-004 | P2 | smbclient/packet fixture for SMBv1/NTLMv1 attempt | host policy baseline | Zeek/SMB downgrade log, L2 |
| F-005 | P0 | DHCP lease manipulation + rogue lease fixture | DHCP scopes/MAC inventory | DHCP/Kea lease log, L3 |
| F-006 | P0 | real LDAP/SMB failed binds then success | AD users/passwords | Samba auth log, L3 |
| F-007 | P0 | nmap/masscan-lite from internal host | host/port inventory | Zeek conn scan pattern, L3 |
| F-008 | P0 | Kerberos/NTLM auth burst against multiple services | AD users/service SPNs | Samba/Kerberos auth log, L3 |
| F-009 | P3 | badge API check-in + AD login from conflicting segment | badge locations/users | badge audit + AD login, L2 |
| F-010 | P0 | service account interactive SMB/RDP-like login | service_accounts.csv | auth log logon_type interactive, L3 |
| F-011 | P0 | net rpc/samba-tool group add/remove | privileged groups | AD group-change audit, L3 |
| F-012 | P2 | API gateway calls with same key from multiple clients | API keys/tokens | Nginx/app/Vault logs, L2 |
| F-013 | P2 | vault kv get loop with real Vault token | Vault policies/secrets | Vault audit log, L3 |
| F-014 | P3 | HR/helpdesk API reset/unlock actions | helpdesk tickets/users | HRIS/helpdesk audit, L2 |
| F-015 | P0 | ssh/winrm-like hop chain across hosts | admin hosts | Zeek/session logs, L2 |
| F-016 | P1 | send real SMTP mails with attachments | mailboxes/DLs/attachments | Postfix log, L3 |
| F-017 | P1 | create forwarding/delegate rule via webmail/API | mailbox rules | Dovecot/Roundcube audit, L2 |
| F-018 | P1 | IMAP login/read another mailbox | mailboxes/delegates | Dovecot audit, L3 |
| F-019 | P1 | send mismatched/encoded attachment | attachment corpus | Postfix/content metadata, L2 |
| F-020 | P1 | send BCC/bulk distribution mail | DLs/mailboxes | Postfix envelope log, L3 |
| F-021 | P1 | send attachment to personal domain sink | personal domains | Postfix outbound log, L3 |
| F-022 | P1 | send attachment to competitor/unknown domain | external domain list | Postfix outbound log, L3 |
| F-023 | P1 | send sensitive-keyword mail | keyword corpus | mail metadata/content log, L2 |
| F-024 | P1 | IMAP fetch old archive messages | old mailbox archive | Dovecot audit, L3 |
| F-025 | P1 | export contacts/address book | contacts seed | Roundcube/webmail audit, L2 |
| F-026 | P2 | send style-deviation mail corpus | writing baseline | mail text audit fixture, L2 |
| F-027 | P2 | send banned phrase mail corpus | policy phrase list | mail content audit, L2 |
| F-028 | P1 | first-time external sensitive email | recipient history | Postfix + recipient history, L2 |
| F-029 | P1 | failed webmail login with personal/unknown account | auth identities | Roundcube auth log, L2 |
| F-030 | P2 | post prompt/upload to AI gateway | confidential docs | AI gateway audit + proxy, L2 |
| F-031 | P2 | paste source code/architecture to AI gateway | repo snippets | AI gateway audit, L2 |
| F-032 | P2 | prompt includes internal host/user/IP data | network inventory | AI gateway audit, L2 |
| F-033 | P2 | access blocked AI domain through Squid | blocked domain list | proxy access log, L3 |
| F-034 | P2 | upload file to AI gateway | upload corpus | AI gateway upload log, L2 |
| F-035 | P2 | ask AI about security procedure/internal process | procedure prompts | AI gateway audit, L2 |
| F-036 | P2 | AI chat contains legal/strategy content | strategy/legal corpus | AI gateway audit, L2 |
| F-037 | P0 | access Samba share outside AD group | AD groups/shares | Samba audit, L3 |
| F-038 | P0 | bulk SMB read/write with smbclient | file corpus | Samba audit + Zeek, L3 |
| F-039 | P0 | mass rename files in SMB share | file corpus | Samba audit rename logs, L3 |
| F-040 | P0 | traverse sensitive directory tree | sensitive dirs | Samba audit path sequence, L3 |
| F-041 | P0 | chmod/setfacl or Samba ACL change | ACL baseline | ACL audit log, L3 |
| F-042 | P2 | create local sensitive files on endpoint volume | classification data | auditd/file inventory, L2 |
| F-043 | P2 | move classified file to public share | classified files | Samba/file classification logs, L3 |
| F-044 | P2 | bulk download wiki/intranet pages | wiki pages | Nginx/wiki access log, L2 |
| F-045 | P0 | real SELECT * / bulk export in Postgres | PII/payroll tables | pg_audit log, L3 |
| F-046 | P1 | run long process/process tree on endpoint | process scripts | auditd/process logs, L2 |
| F-047 | P1 | call internal API unusual endpoint pattern | API users/endpoints | Nginx/app logs, L3 |
| F-048 | P0 | generate HTTP 401/403/404 spike | API credentials | Nginx access log, L3 |
| F-049 | P0 | git clone/fetch many Gitea repos | seeded repos | Gitea access/audit log, L3 |
| F-050 | P1 | change suppress rule in SIEM/admin UI | SIEM users/rules | admin audit log, L2 |
| F-051 | P1 | login/use hypervisor console | admin users/assets | hypervisor/cockpit audit, L2 |
| F-052 | P1 | create cron/systemd service in endpoint | endpoint scripts | auditd/journald logs, L2 |
| F-053 | P1 | disable backup/delete snapshot fixture | backup metadata | backup audit log, L2 |
| F-054 | P1 | run encoded or bypass command | command corpus | auditd/process command log, L2 |
| F-055 | P0 | mount USB-like volume + copy file | USB IDs/files | auditd/file write log, L2 |
| F-056 | P3 | submit CUPS print job for sensitive doc | print docs/classification | CUPS log, L2 |
| F-057 | P0 | toggle promiscuous mode in privileged endpoint | NIC baseline | auditd/ip link log, L2 |
| F-058 | P2 | stop/disable DLP health agent | DLP agent seed | DLP health audit, L2 |
| F-059 | P2 | clipboard API/write large clipboard event | clipboard corpus | endpoint activity log, L2 |
| F-060 | P2 | screenshot generator bursts | screenshot metadata | endpoint activity log, L2 |
| F-061 | P2 | contact unusual servers for role | role/server map | Zeek/session logs, L3 |
| F-062 | P2 | search risky terms in SIEM/log UI | keyword list | SIEM search audit, L2 |
| F-063 | P0 | login from unknown device ID | device inventory | AD/auth device log, L2 |
| F-064 | P2 | compress normal activity into short window | baseline schedule | activity logs, L2 |
| F-065 | P2 | access dormant system/app | access history | app/Samba logs, L2 |
| F-066 | P2 | generate peer-group outlier activity | peer_groups.yml | multi-source activity logs, L2 |
| F-067 | P2 | upload large file to MinIO/personal cloud via proxy | cloud bucket/files | proxy + MinIO logs, L3 |
| F-068 | P2 | high volume transfer to first-seen external sink | destination history | proxy log, L3 |
| F-069 | P2 | proxy CONNECT/tunnel-like traffic | protocol list | Squid/proxy log, L3 |
| F-070 | P3 | badge event and conflicting system login | badge locations | badge + auth logs, L2 |
| F-071 | P3 | run multi-signal scenario bundle | cross-signal seeds | combined evidence, L2 |
| F-072 | P3 | offboarded user performs AD/app activity | offboarding.csv | HRIS + auth/app logs, L2 |
| F-073 | P3 | multiple users access same file/record chain | file/record IDs | Samba/app logs, L2 |
| F-074 | P3 | after-hours badge + login | shift calendar | badge + auth logs, L2 |
| F-075 | P3 | new hire accesses many systems | employees.csv | HRIS + app logs, L2 |
| F-076 | P3 | role-changed user uses old entitlement | role_changes.csv | HRIS + auth/app logs, L2 |
| F-077 | P3 | user on leave performs activity | leave_calendar.csv | HRIS + auth/app logs, L2 |
| F-078 | P3 | contractor accesses out-of-scope app | contractor scopes | HRIS + app logs, L2 |
| F-079 | P0 | real after-hours login | work_windows.yml | AD/auth log, L2 |
| F-080 | P0 | long session with no input events | session/input logs | endpoint activity log, L2 |
| F-081 | P0 | role work-window deviation activity | role work windows | auth/activity log, L2 |

---

## 7. Fazlar

### RI-0 — Real Parity Foundation

Hedef:

- Mevcut synthetic coverage bozulmadan real integration katmani eklenir.
- `features.yml` icine `real_parity_level`, `real_tool`, `real_action_command`,
  `raw_log_assertion`, `ingest_assertion` alanlari eklenir.
- `reports/real/` rapor dizini ve real coverage scriptleri olusur.

Test:

```bash
make test-all
make real-coverage
pytest tests/real/test_real_catalog.py
```

### RI-1 — Real Identity, File, DNS, DHCP, Network

Oncelik: P0 core.

Yapilacak:

- Samba4 AD real profile'i stabil hale getir.
- Samba file server full_audit aktif olsun.
- BIND query log gercek sorgulari yazsin.
- DHCP/Kea lease loglari test edilsin.
- Zeek gercek veya replay-generated network traffic loglarini uretsin.
- Seed: users, groups, service accounts, devices, files, DNS records.

Feature hedefi:

- F-001, F-002, F-003, F-005, F-006, F-007, F-008, F-010, F-011,
  F-015, F-037, F-038, F-039, F-040, F-041, F-055, F-057,
  F-063, F-079, F-080, F-081

Test:

```bash
make real-up
make seed-real-identity
make seed-real-files
pytest tests/real/test_identity_file_network.py
pytest tests/real/features -m p0
make real-coverage
```

### RI-2 — Real Mail, DB, Git, Web/API

Oncelik: P1 + P0 app features.

Yapilacak:

- Postfix/Dovecot/Roundcube real mail path.
- PostgreSQL pg_audit real audit path.
- Gitea seeded repos and real clone/fetch.
- Nginx/internal app real access/error logs.
- Seed: mailboxes, DLs, attachments, DB tables, repos, API users.

Feature hedefi:

- F-016..F-029
- F-045, F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054

Test:

```bash
make seed-real-mail
make seed-real-apps
pytest tests/real/test_mail_db_git_web.py
pytest tests/real/features -m p1
make real-coverage
```

### RI-3 — Real Security, Secrets, Proxy, AI, Cloud, Endpoint Behavior

Oncelik: P2.

Yapilacak:

- Vault OSS audit log.
- Squid proxy + MinIO/object storage.
- Audited AI gateway/Open WebUI-like endpoint.
- DLP health service.
- Endpoint auditd/activity generator real actions.
- Seed: tokens, secrets, blocked domains, AI prompts, upload files, peer baselines.

Feature hedefi:

- F-012, F-013, F-030..F-036, F-042, F-043, F-044, F-058,
  F-059, F-060, F-061, F-062, F-064, F-065, F-066, F-067, F-068, F-069

Test:

```bash
make seed-real-security
make seed-real-endpoint
pytest tests/real/test_security_proxy_ai_endpoint.py
pytest tests/real/features -m p2
make real-coverage
```

### RI-4 — Real Physical, HR, Collaboration, Print, CRM

Oncelik: P3.

Yapilacak:

- HRIS real-like app with DB-backed audit.
- Badge API DB-backed audit.
- CUPS real print jobs.
- Mattermost real container or audited collaboration endpoint.
- SuiteCRM/CRM real-like access/export logs.
- Seed: employees, leave, offboarding, role changes, badge locations.

Feature hedefi:

- F-009, F-014, F-056, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-077, F-078

Test:

```bash
make seed-real-physical-hr
pytest tests/real/test_physical_hr_collab_print.py
pytest tests/real/features -m p3
make real-coverage
```

### RI-5 — Real Scenario Replay 83/83

Hedef:

- S-001..S-083 icin `real-scenario` replay.
- Scenario replay, feature replay'lerin gercek aksiyonlarini orkestre eder.
- Positive + negative scenario evidence real logs ile dogrulanir.

Test:

```bash
pytest tests/real/scenario
make real-scenario-coverage
```

### RI-6 — Real Ingest Gate

Hedef:

- Filebeat/Logstash/Elasticsearch veya Wazuh pipeline gercek loglari toplar.
- En az 40 core/high-value feature icin L3 assertion vardir.
- Tum feature'lar icin en az L2 assertion vardir.

Test:

```bash
make test-real-ingest
make test-real-all
```

---

## 8. Kabul Kriterleri

Final kabul:

```text
[ ] Synthetic test-all hala PASS
[ ] real-up ile real profile servisleri boot ediyor
[ ] seed-real-all idempotent
[ ] 81 feature real positive PASS
[ ] 81 feature real negative PASS
[ ] 83 scenario real positive PASS
[ ] 83 scenario real negative PASS
[ ] 81 feature L2 veya ustu
[ ] En az 40 feature L3
[ ] Waiver yok
[ ] reports/real/coverage final PASS
```

Testsiz, raw-log assertionsiz veya seed datasiz real integration teslimi kabul
edilmez.

