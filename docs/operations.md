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

## Case management

```bash
wt cases list
wt cases show <case_id>
wt alerts show <alert_id>          # includes score breakdown
wt cases assign <case_id> <user>
wt cases comment <case_id> "text"
wt cases link-ticket <case_id> INC-123
wt cases timeline <case_id>
wt cases export <case_id> --format md -o report.md
wt cases show <case_id> --explain  # LLM narrative; severity unchanged
```

Closing as `false_positive` records `feedback_submitted` on the timeline with `pending_rule_id`.

## Connectors (production)

| Connector | Auth / TLS | Pagination |
|-----------|------------|------------|
| `file_jsonl` | local path | byte offset + rotation/truncation detection |
| `elasticsearch` | basic / bearer / api_key, `ca_cert_path`, `verify_tls` | `search_after` |
| `wazuh` | token or username/password → token | offset + `timestamp>` window |
| `server_stack` | read-only lab logs | file index + offset |

Shared HTTP settings per source config: `timeout_seconds`, `max_retries`, `backoff_base_seconds`.

Ingest results include `latency_ms` and `http_retries` for audit/daemon summaries.

## Graph checkpoint & approval resume

Production default: durable SQLite checkpoints at `WATCHTOWER_GRAPH_CHECKPOINT_PATH` (separate from product DB).

```bash
wt graph interrupted
wt graph resume --thread-id <thread_id> --decision approved --approver-id sec-1
wt graph checkpoint-prune --retention-days 30
```

Set `WATCHTOWER_GRAPH_CHECKPOINT_USE_MEMORY=true` only for local dev/tests. After process restart, interrupted runs resume from disk via `Command(resume=...)`.

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
