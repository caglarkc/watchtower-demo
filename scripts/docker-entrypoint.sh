#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$(dirname "${WATCHTOWER_DATABASE_PATH:-/data/watchtower.db}")"
mkdir -p "${WATCHTOWER_BACKUP_DIR:-/backups}"

wt migrate upgrade

exec "$@"
