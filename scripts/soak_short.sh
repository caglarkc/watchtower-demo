#!/usr/bin/env bash
# CI-friendly short soak: real F-001 replay through daemon loop + metrics evidence.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WT="${ROOT}/.venv/bin/wt"
if [ ! -x "$WT" ]; then
  WT="wt"
fi

UV="${ROOT}/.venv/bin/python"
if [ ! -x "$UV" ]; then
  UV="python3"
fi

REPORT_DIR="${SOAK_REPORT_DIR:-$ROOT/reports/soak}"
mkdir -p "$REPORT_DIR"
DB_PATH="${SOAK_DB:-$ROOT/data/soak_short.db}"
export WATCHTOWER_DATABASE_PATH="$DB_PATH"
rm -f "$DB_PATH"
mkdir -p "$(dirname "$DB_PATH")"

ADMIN_PASS="${WATCHTOWER_BOOTSTRAP_PASSWORD:-soak-short-password}"

"$WT" migrate upgrade
"$WT" bootstrap -u soak-admin -e soak@localhost --password "$ADMIN_PASS"

JSONL="${SOAK_JSONL:-$ROOT/data/soak_f001.jsonl}"
"$UV" scripts/soak_prepare_f001.py --db "$DB_PATH" --jsonl "$JSONL" --mode learn

ITERATIONS="${SOAK_ITERATIONS:-4}"
for i in $(seq 1 "$ITERATIONS"); do
  echo "soak daemon iteration $i/$ITERATIONS"
  "$WT" daemon run --once \
    --ingest-limit "${SOAK_INGEST_LIMIT:-100}" \
    --pipeline-limit "${SOAK_PIPELINE_LIMIT:-200}" \
    --graph-limit "${SOAK_GRAPH_LIMIT:-20}"
done

"$WT" metrics --json > "$REPORT_DIR/short_soak_metrics.json"
"$WT" health --json > "$REPORT_DIR/short_soak_health.json"

"$UV" scripts/soak_report.py \
  --db "$DB_PATH" \
  --output "$REPORT_DIR/short_soak_summary.json" \
  --label short_soak

"$WT" health readiness \
  -o "$REPORT_DIR/short_soak_readiness.json" \
  --soak-report "$REPORT_DIR/short_soak_summary.json"

echo "Short soak complete. Reports in $REPORT_DIR"
