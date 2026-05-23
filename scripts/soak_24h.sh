#!/usr/bin/env bash
# Long soak: resumable daemon loop with server-stack or F-001 JSONL source.
# Run outside CI: SOAK_HOURS=24 ./scripts/soak_24h.sh
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
DB_PATH="${SOAK_DB:-$ROOT/data/soak_24h.db}"
export WATCHTOWER_DATABASE_PATH="$DB_PATH"
STATE_FILE="${SOAK_STATE_FILE:-$REPORT_DIR/soak_24h_state.json}"
LOG_FILE="${SOAK_LOG_FILE:-$REPORT_DIR/soak_24h.log}"
SUMMARY_FILE="${SOAK_SUMMARY_FILE:-$REPORT_DIR/soak_24h_summary.json}"

HOURS="${SOAK_HOURS:-24}"
INTERVAL="${WATCHTOWER_DAEMON_INGEST_INTERVAL_SECONDS:-60}"
END=$((SECONDS + HOURS * 3600))

if [ ! -f "$DB_PATH" ]; then
  ADMIN_PASS="${WATCHTOWER_BOOTSTRAP_PASSWORD:-soak-24h-password}"
  "$WT" migrate upgrade
  "$WT" bootstrap -u soak-admin -e soak@localhost --password "$ADMIN_PASS"
  JSONL="${SOAK_JSONL:-$ROOT/data/soak_24h_f001.jsonl}"
  "$UV" scripts/soak_prepare_f001.py --db "$DB_PATH" --jsonl "$JSONL" --mode learn
  echo '{"iteration":0,"started_at":"'$(date -Is)'"}' > "$STATE_FILE"
fi

iteration=0
if [ -f "$STATE_FILE" ]; then
  iteration=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('iteration',0))" 2>/dev/null || echo 0)
fi

echo "Starting ${HOURS}h soak (interval=${INTERVAL}s). state=$STATE_FILE log=$LOG_FILE" | tee -a "$LOG_FILE"

while [ "$SECONDS" -lt "$END" ]; do
  iteration=$((iteration + 1))
  ts=$(date -Is)
  echo "$ts iteration=$iteration" | tee -a "$LOG_FILE"
  if ! "$WT" daemon run --once >> "$LOG_FILE" 2>&1; then
    echo "$ts daemon iteration failed (continuing)" | tee -a "$LOG_FILE"
  fi
  "$WT" health --json >> "$LOG_FILE" 2>&1 || true
  printf '{"iteration":%s,"last_at":"%s"}\n' "$iteration" "$ts" > "$STATE_FILE"
  sleep "$INTERVAL"
done

"$WT" metrics --json > "$REPORT_DIR/soak_24h_metrics.json" 2>>"$LOG_FILE" || true
"$UV" scripts/soak_report.py \
  --db "$DB_PATH" \
  --output "$SUMMARY_FILE" \
  --label soak_24h || true

"$WT" health readiness \
  -o "$REPORT_DIR/soak_24h_readiness.json" \
  --soak-report "$SUMMARY_FILE" 2>>"$LOG_FILE" || true

echo "24h soak finished. state=$STATE_FILE summary=$SUMMARY_FILE log=$LOG_FILE"
