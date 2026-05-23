# Watchtower

UEBA product for closed-network enterprise deployments. CLI-first operator workflow.

## Quick start

```bash
cp .env.example .env
pip install -e ".[dev]"
./scripts/fresh_install.sh
wt health
```

See [docs/install.md](docs/install.md) and [docs/operations.md](docs/operations.md).

## Docker

```bash
docker compose config
docker compose up -d --build
```

## Tests

```bash
pytest tests/ -q
pytest tests/production tests/load -v
```
