#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p logs

# Stop existing bot if running
if [[ -f logs/bot.pid ]]; then
  oldpid="$(cat logs/bot.pid || true)"
  if [[ -n "${oldpid}" ]] && ps -p "$oldpid" >/dev/null 2>&1; then
    echo "Stopping existing bot pid=$oldpid"
    kill "$oldpid" || true
    sleep 1
  fi
fi

echo "Starting bot (caffeinate + python3 -u runner_5m.py)..."
# Start bot and record PYTHON pid
caffeinate -dims python3 -u runner_5m.py >> logs/bot.log 2>&1 &
echo $! > logs/bot.pid

echo "Started bot pid=$(cat logs/bot.pid)"
echo "Logs: tail -f logs/bot.log"
