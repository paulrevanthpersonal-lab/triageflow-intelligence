#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHROME_BIN="${CHROME_BIN:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
NODE_BIN="${NODE_BIN:-node}"
DEFAULT_PYTHON="$PROJECT_ROOT/.venv/bin/python"
if [[ ! -x "$DEFAULT_PYTHON" ]]; then DEFAULT_PYTHON="python3"; fi
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON}"
PORT="${PORT:-8024}"
OUTPUT_DIR="$PROJECT_ROOT/docs/screenshots"
TEMP_PROFILE="$(mktemp -d)"

mkdir -p "$OUTPUT_DIR"
cd "$PROJECT_ROOT"
TRIAGEFLOW_DB_PATH="$TEMP_PROFILE/screenshots.db" \
  "$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" >"$TEMP_PROFILE/server.log" 2>&1 &
SERVER_PID=$!
cleanup(){ kill "$SERVER_PID" 2>/dev/null || true; rm -rf "$TEMP_PROFILE"; }
trap cleanup EXIT

READY=0
for _ in {1..80}; do
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    echo "Application process stopped before readiness" >&2
    sed -n '1,160p' "$TEMP_PROFILE/server.log" >&2
    exit 1
  fi
  if curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null; then READY=1; break; fi
  sleep 0.25
done
if [[ "$READY" -ne 1 ]]; then
  echo "Application did not become ready" >&2
  sed -n '1,160p' "$TEMP_PROFILE/server.log" >&2
  exit 1
fi

BASE_URL="http://127.0.0.1:$PORT" CHROME_BIN="$CHROME_BIN" "$NODE_BIN" scripts/capture_screenshots.mjs

echo "Captured 10 product screenshots in $OUTPUT_DIR"
