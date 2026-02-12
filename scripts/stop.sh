#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f logs/bot.pid ]]; then
  echo "No logs/bot.pid found. Bot not running?"
  exit 0
fi

pid="$(cat logs/bot.pid || true)"
if [[ -z "${pid}" ]]; then
  echo "bot.pid is empty."
  exit 1
fi

if ps -p "$pid" >/dev/null 2>&1; then
  echo "Stopping bot pid=$pid"
  kill "$pid" || true
  sleep 1
  if ps -p "$pid" >/dev/null 2>&1; then
    echo "Bot still running, forcing stop..."
    kill -9 "$pid" || true
  fi
else
  echo "Bot pid=$pid not running."
fi

rm -f logs/bot.pid
echo "Stopped."
