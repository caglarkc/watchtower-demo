# Watchtower — Closed-Network Install

## Prerequisites

- Python 3.11+ or Docker
- SQLite data volume (`/data` in container)
- Read-only access to log sources (JSONL, Elasticsearch, Wazuh, server-stack lab)

## Docker (recommended)

```bash
cp .env.example .env
# Edit secrets and paths
docker compose config
docker compose build
docker compose run --rm watchtower wt bootstrap -u admin -e admin@corp.local
docker compose up -d
docker compose exec watchtower wt health --json
```

## Bare metal

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
./scripts/fresh_install.sh
```

## Source onboarding

```bash
wt sources register -t file_jsonl -n "AD JSONL" -c '{"file_path":"/data/ad.jsonl"}'
wt sources register -t server_stack -n "Lab logs" -c '{"logs_root":"/lab/server-stack/logs"}'
wt sources health
```

## Provider onboarding

```bash
wt providers list
wt providers set-chain gemini,ollama
wt providers clear-chain
```

## Upgrade

```bash
./scripts/upgrade.sh
```
