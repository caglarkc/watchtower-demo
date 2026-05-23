# Watchtower — Operations

## Health

```bash
wt health
wt health --json   # container HEALTHCHECK
```

## Backup / restore

```bash
wt backup create
wt backup list
wt backup restore /backups/watchtower-YYYYMMDDTHHMMSS.db --yes
```

## Retention

Configured via `.env` (`WATCHTOWER_RETENTION_*_DAYS`).

```bash
wt retention apply --dry-run
wt retention apply
```

## Migrations

```bash
wt migrate status
wt migrate upgrade
```

## Soak tests

CI-friendly short soak:

```bash
./scripts/soak_short.sh
```

Long daemon soak (documented, not CI):

```bash
SOAK_HOURS=24 ./scripts/soak_24h.sh
```

## Security notes

- No auto-remediation: Watchtower observes and alerts only.
- Audit logs mask secrets (`password`, `api_key`, `token`, …).
- Connectors are read-only (poll + cursor ack only).
- Multi-tenant queries require `tenant_id` scoping on repositories.
