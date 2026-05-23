#!/usr/bin/env bash
# Fresh install: migrations + bootstrap admin (non-interactive password via env).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_PATH="${WATCHTOWER_DATABASE_PATH:-$ROOT/data/watchtower.db}"
export WATCHTOWER_DATABASE_PATH="$DB_PATH"
ADMIN_PASS="${WATCHTOWER_BOOTSTRAP_PASSWORD:-changeme-change-in-production}"

mkdir -p "$(dirname "$DB_PATH")"

wt migrate upgrade
wt bootstrap -u admin -e admin@localhost --password "$ADMIN_PASS"
wt health --json
wt status

echo "Fresh install complete. Database: $DB_PATH"
