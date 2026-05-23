# Production Readiness Report — Faz 11

## Delivered

| Area | Status | Notes |
|------|--------|-------|
| Docker / Compose | Done | `Dockerfile`, `docker-compose.yml`, entrypoint runs migrations |
| `.env.example` | Done | DB, sources, providers, mode, retention |
| Source onboarding | Done | `wt sources register` |
| Provider onboarding | Done | `wt providers list/set-chain/clear-chain` |
| Backup / restore | Done | `wt backup *`, SQLite online backup |
| Migration upgrade | Done | `wt migrate status/upgrade` |
| Retention | Done | `wt retention apply`, migration `009_production` |
| Health checks | Done | `wt health [--json]`; metrics-linked degraded reasons |
| Runtime metrics | Done | `wt metrics [--json]`; counters in `runtime_metrics` table |
| Structured logs | Done | JSON lines with tenant/source/run_id/event_counts; secrets masked |
| Soak / load | Done | `scripts/soak_short.sh` (real daemon + F-001), `soak_24h.sh` (resumable) |
| Readiness JSON | Done | `wt health readiness -o …` merges health + metrics + soak summary |
| Security audit tests | Done | `tests/production/test_security_audit.py` |

## Gates

Run before release:

```bash
docker compose config
pytest tests/production tests/load -v
./scripts/soak_short.sh
./scripts/fresh_install.sh
./scripts/upgrade.sh
wt health readiness -o reports/soak/readiness.json
```

## Remaining risks

- Single-tenant bootstrap CLI (multi-tenant DB supported; second tenant via API/DB only).
- LLM providers without API keys → fail-open (by design).
- 24h soak is operator-run, not CI (use `soak_short.sh` in CI).
- Elasticsearch/Wazuh connectors need network reachability from container.
