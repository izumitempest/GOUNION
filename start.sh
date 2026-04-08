#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  GoUnion — Dev Startup Script (Linux / macOS)
# ─────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$SCRIPT_DIR/gounion-remake"
VENV_DIR="$SCRIPT_DIR/venv"
ENV_FILE="$SCRIPT_DIR/.env"

# ── Colours ──────────────────────────────────
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

log()  { echo -e "${CYAN}[GoUnion]${RESET} $1"; }
ok()   { echo -e "${GREEN}[  OK  ]${RESET} $1"; }
warn() { echo -e "${YELLOW}[ WARN ]${RESET} $1"; }
err()  { echo -e "${RED}[ ERR  ]${RESET} $1"; }

# ── Cleanup on exit ───────────────────────────
PIDS=()
cleanup() {
  echo ""
  log "Shutting down servers..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null && ok "Killed PID $pid"
  done
  exit 0
}
trap cleanup SIGINT SIGTERM

# ── Pre-flight checks ─────────────────────────
log "Starting GoUnion development environment..."

if [ ! -f "$ENV_FILE" ]; then
  warn ".env file not found at $ENV_FILE"
  warn "Backend may start without required environment variables."
fi

# ── Backend ───────────────────────────────────
log "Setting up Python virtual environment..."

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
  ok "Created virtual environment"
fi

source "$VENV_DIR/bin/activate"

log "Installing / verifying Python dependencies..."
pip install -r "$BACKEND_DIR/requirements.txt" -q
ok "Python dependencies ready"

log "Starting FastAPI backend on http://127.0.0.1:8001 ..."
cd "$BACKEND_DIR"
uvicorn fastapi_server.main:app --port 8001 --reload &
BACKEND_PID=$!
PIDS+=("$BACKEND_PID")
ok "Backend started (PID $BACKEND_PID)"

# ── Frontend ──────────────────────────────────
log "Checking Node.js dependencies..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  log "node_modules not found — running npm install..."
  npm install
  ok "npm install complete"
fi

log "Starting Vite frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!
PIDS+=("$FRONTEND_PID")
ok "Frontend started (PID $FRONTEND_PID)"

# ── Done ──────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${GREEN}  GoUnion is running!${RESET}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  Frontend  →  ${CYAN}http://localhost:3000${RESET}"
echo -e "  Backend   →  ${CYAN}http://127.0.0.1:8001${RESET}"
echo -e "  API Docs  →  ${CYAN}http://127.0.0.1:8001/docs${RESET}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "  Press ${YELLOW}Ctrl+C${RESET} to stop all servers"
echo ""

# Wait for any child process to exit
wait
