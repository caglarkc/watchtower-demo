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

## Daemon pipeline

Single runtime loop: source poll → raw store → normalize → candidate → graph → alert/silent finding.

```bash
# One iteration (CI / smoke)
wt daemon run --once

# Bounded iterations
wt daemon run --max-iterations 1

# Continuous (default interval from WATCHTOWER_DAEMON_INGEST_INTERVAL_SECONDS)
wt daemon run
```

Graceful shutdown: `SIGINT` / `SIGTERM` finish the current iteration then exit.

Per-source options in source `config` JSON: `poll_limit`, `backoff_base_seconds`, `backoff_max_seconds`.

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
