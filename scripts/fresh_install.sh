#!/usr/bin/env bash
# Fresh install: migrations + bootstrap admin (non-interactive password via env).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WT="${ROOT}/.venv/bin/wt"
if [ ! -x "$WT" ]; then
  WT="wt"
fi

DB_PATH="${WATCHTOWER_DATABASE_PATH:-$ROOT/data/watchtower.db}"
export WATCHTOWER_DATABASE_PATH="$DB_PATH"
ADMIN_PASS="${WATCHTOWER_BOOTSTRAP_PASSWORD:-changeme-change-in-production}"

mkdir -p "$(dirname "$DB_PATH")"

"$WT" migrate upgrade
"$WT" bootstrap -u admin -e admin@localhost --password "$ADMIN_PASS"
"$WT" health --json
"$WT" status

echo "Fresh install complete. Database: $DB_PATH"
