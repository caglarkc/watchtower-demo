#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v inotifywait >/dev/null 2>&1; then
  echo "Missing dependency: inotifywait"
  echo "Install with: sudo apt-get install inotify-tools"
  exit 1
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "This script must run inside a git repository."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Git remote 'origin' is not configured."
  exit 1
fi

BRANCH="${AUTO_PUSH_BRANCH:-$(git branch --show-current)}"
DEBOUNCE_SECONDS="${AUTO_PUSH_DEBOUNCE:-2}"
COMMIT_PREFIX="${AUTO_PUSH_COMMIT_PREFIX:-auto: sync}"
LOCK_DIR="$SCRIPT_DIR/.git/.auto-push-lock"

if [[ -z "$BRANCH" ]]; then
  echo "Could not detect the current git branch."
  exit 1
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Auto push watcher is already running for this repository."
  exit 1
fi

cleanup() {
  rmdir "$LOCK_DIR" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

sync_changes() {
  git add -A

  if git diff --cached --quiet; then
    return 0
  fi

  local commit_msg
  commit_msg="$COMMIT_PREFIX $(date '+%Y-%m-%d %H:%M:%S')"
  git commit -m "$commit_msg"
  git push origin "$BRANCH"
  echo "Pushed: $commit_msg"
}

echo "Auto push watcher started in: $SCRIPT_DIR"
echo "Branch: $BRANCH"
echo "Debounce: ${DEBOUNCE_SECONDS}s"
echo "Press Ctrl+C to stop."

sync_changes

while true; do
  inotifywait -qq -r \
    -e modify,create,delete,move \
    --exclude '(\.git/|node_modules/|\.venv/|dist/|build/|\.next/|__pycache__/|\.pytest_cache/|\.mypy_cache/|\.ruff_cache/|\.coverage|htmlcov/|\.DS_Store$|.*\.swp$|.*~$)' \
    "$SCRIPT_DIR"

  sleep "$DEBOUNCE_SECONDS"
  sync_changes
done
