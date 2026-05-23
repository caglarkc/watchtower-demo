# Watchtower Closed Server Stack

Kapalı `corp-lan` simülasyon ortamı (Phase 1: kimlik, dosya, DNS, DHCP, endpoint, ağ akışı).

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
