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
| Health checks | Done | `wt health [--json]` |
| Soak / load | Done | `scripts/soak_*.sh`, `tests/load/` |
| Security audit tests | Done | `tests/production/test_security_audit.py` |

## Gates

Run before release:

```bash
docker compose config
pytest tests/production tests/load -v
./scripts/fresh_install.sh
./scripts/upgrade.sh
```

## Remaining risks

- Single-tenant bootstrap CLI (multi-tenant DB supported; second tenant via API/DB only).
- LLM providers without API keys → fail-open (by design).
- 24h soak is operator-run, not CI (use `soak_short.sh` in CI).
- Elasticsearch/Wazuh connectors need network reachability from container.
