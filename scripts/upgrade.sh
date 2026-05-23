#!/usr/bin/env bash
# Upgrade path: backup then apply pending migrations.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export WATCHTOWER_DATABASE_PATH="${WATCHTOWER_DATABASE_PATH:-$ROOT/data/watchtower.db}"

wt backup create
wt migrate status
wt migrate upgrade
wt health --json

echo "Upgrade complete."
