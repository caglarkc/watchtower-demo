#!/usr/bin/env bash
# CI-friendly short soak: health + optional ingest loops.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WT="${ROOT}/.venv/bin/wt"
if [ ! -x "$WT" ]; then
  WT="wt"
fi

ITERATIONS="${SOAK_ITERATIONS:-12}"
SLEEP_SEC="${SOAK_SLEEP_SECONDS:-2}"

for i in $(seq 1 "$ITERATIONS"); do
  echo "soak iteration $i/$ITERATIONS"
  "$WT" health --json
  sleep "$SLEEP_SEC"
done

echo "Short soak complete ($ITERATIONS iterations)."
