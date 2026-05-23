#!/usr/bin/env bash
# Long soak for closed-network daemon validation (24h default).
# Run outside CI: SOAK_HOURS=24 ./scripts/soak_24h.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

HOURS="${SOAK_HOURS:-24}"
INTERVAL="${WATCHTOWER_DAEMON_INGEST_INTERVAL_SECONDS:-60}"
END=$((SECONDS + HOURS * 3600))

echo "Starting ${HOURS}h soak (interval=${INTERVAL}s). Logs: soak.log"

while [ "$SECONDS" -lt "$END" ]; do
  date -Is | tee -a soak.log
  wt health --json >> soak.log 2>&1 || true
  # Poll first enabled source if any (graceful on outage)
  wt sources list 2>/dev/null | awk 'NR>1 {print $1; exit}' | while read -r sid; do
    [ -n "$sid" ] && wt ingest once --source "$sid" >> soak.log 2>&1 || true
  done
  sleep "$INTERVAL"
done

echo "24h soak finished. Review soak.log"
