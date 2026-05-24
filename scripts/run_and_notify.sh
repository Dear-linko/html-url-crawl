#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
LOG_FILE="$LOG_DIR/run_and_notify.log"
LOCK_DIR="${TMPDIR:-/tmp}/html-url-crawl.lock"

mkdir -p "$LOG_DIR"
cd "$ROOT_DIR"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [warn] run_and_notify already running; skipping" >> "$LOG_FILE" 2>&1
  exit 0
fi

cleanup() {
  rmdir "$LOCK_DIR" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.env"
  set +a
fi

{
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] start run_and_notify"
  make check-update
  .venv/bin/python scripts/render_report.py
  bash "$ROOT_DIR/sync-reports.sh"
  .venv/bin/python scripts/notify_telegram.py
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] done run_and_notify"
} >> "$LOG_FILE" 2>&1
