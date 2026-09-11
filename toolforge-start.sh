#!/bin/sh
set -eu

BACKEND_PORT="${BACKEND_PORT:-8001}"

PORT="$BACKEND_PORT" HOST="127.0.0.1" python server/run.py &
backend_pid=$!

cleanup() {
  kill "$backend_pid" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

export BACKEND_API_URL="${BACKEND_API_URL:-http://127.0.0.1:${BACKEND_PORT}}"
export HOST="${HOST:-0.0.0.0}"
exec node toolforge-server.mjs