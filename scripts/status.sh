#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f logs/bot.pid ]]; then
  echo "Status: STOPPED (no logs/bot.pid)"
  exit 0
fi

pid="$(cat logs/bot.pid || true)"
if [[ -z "${pid}" ]]; then
  echo "Status: UNKNOWN (empty pid file)"
  exit 1
fi

if ps -p "$pid" >/dev/null 2>&1; then
  echo "Status: RUNNING pid=$pid"
  ps -p "$pid" -o pid,ppid,etime,command
else
  echo "Status: DEAD (pid file exists but process not running) pid=$pid"
  exit 1
fi
