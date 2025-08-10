#!/usr/bin/env bash
# Launch backend (FastAPI) and frontend (Vite) accessible from local network
# - Detects local IPv4 and sets ALLOWED_ORIGINS for CORS
# - Runs uvicorn on 0.0.0.0:8000 using .venv
# - Runs Vite with --host so it listens on all interfaces
set -euo pipefail

# Resolve repo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

get_ip() {
  if command -v ip >/dev/null 2>&1; then
    ip -4 route get 1.1.1.1 2>/dev/null | awk '/src/ {print $7; exit}'
  elif command -v hostname >/dev/null 2>&1; then
    hostname -I 2>/dev/null | awk '{print $1}'
  else
    echo "127.0.0.1"
  fi
}

IP="$(get_ip)"
FRONTEND_ORIGIN="http://$IP:5173"
export ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173,${FRONTEND_ORIGIN}"
echo "Using ALLOWED_ORIGINS=${ALLOWED_ORIGINS}"

# Pick Python from .venv (support UNIX and Windows layouts)
PY_BIN="$REPO_ROOT/.venv/bin/python"
if [[ ! -x "$PY_BIN" && -x "$REPO_ROOT/.venv/Scripts/python.exe" ]]; then
  PY_BIN="$REPO_ROOT/.venv/Scripts/python.exe"
fi
if [[ ! -x "$PY_BIN" ]]; then
  echo "Error: .venv Python not found in $REPO_ROOT/.venv" >&2
  exit 1
fi

BACKEND_CMD=("$PY_BIN" -m uvicorn app.app:app --reload --host 0.0.0.0 --port 8000)
FRONTEND_CMD=(npm run dev -- --host)

echo "Backend URL:   http://$IP:8000"
echo "Frontend URL:  http://$IP:5173"

# Start backend
pushd "$REPO_ROOT" >/dev/null
"${BACKEND_CMD[@]}" &
BACKEND_PID=$!
popd >/dev/null

# Start frontend
pushd "$REPO_ROOT/frontend" >/dev/null
"${FRONTEND_CMD[@]}" &
FRONTEND_PID=$!
popd >/dev/null

cleanup() {
  echo "\nStopping services..."
  kill "$BACKEND_PID" 2>/dev/null || true
  kill "$FRONTEND_PID" 2>/dev/null || true
  wait "$BACKEND_PID" 2>/dev/null || true
  wait "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Services launched. Press Ctrl+C to stop both."
# Wait on both PIDs
wait
