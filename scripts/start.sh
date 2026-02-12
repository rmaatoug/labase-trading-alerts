#!/usr/bin/env bash
set -euo pipefail

# Load .env if present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

cd "$(dirname "$0")/.."
mkdir -p logs

# Optional caffeinate on macOS to prevent system sleep during long runs.
CAF_PID=""
if [ "$(uname)" = "Darwin" ] && command -v caffeinate >/dev/null 2>&1; then
  echo "Starting caffeinate (macOS)..."
  caffeinate -dimsu &
  CAF_PID=$!
fi

# Stop existing bot if running
if [[ -f logs/bot.pid ]]; then
  oldpid="$(cat logs/bot.pid || true)"
  if [[ -n "${oldpid}" ]] && ps -p "$oldpid" >/dev/null 2>&1; then
    echo "Stopping existing bot pid=$oldpid"
    kill "$oldpid" || true
    sleep 1
  fi
fi

echo "Starting bot (python3 -u runner_5m.py)..."
# Start bot and record PYTHON pid
python3 -u runner_5m.py >> logs/bot.log 2>&1 &
echo $! > logs/bot.pid

echo "Started bot pid=$(cat logs/bot.pid)"
echo "Logs: tail -f logs/bot.log"

# Cleanup caffeinate if started
cleanup() {
  if [ -n "${CAF_PID}" ]; then
    kill "${CAF_PID}" || true
  fi
}
trap cleanup EXIT
