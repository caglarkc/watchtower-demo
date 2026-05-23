#!/usr/bin/env bash
# Upgrade path: backup then apply pending migrations.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WT="${ROOT}/.venv/bin/wt"
if [ ! -x "$WT" ]; then
  WT="wt"
fi

export WATCHTOWER_DATABASE_PATH="${WATCHTOWER_DATABASE_PATH:-$ROOT/data/watchtower.db}"

"$WT" backup create
"$WT" migrate status
"$WT" migrate upgrade
"$WT" health --json

echo "Upgrade complete."
