# --- AUTO-ADDED: logging + metrics ---
from infra.logger import setup_logger
from infra.metrics import load_metrics, inc

logger = setup_logger("logs/bot.log")
metrics = load_metrics()
logger.info("RUNNER START")
# --- END AUTO-ADDED ---

import subprocess
import sys
import time
from datetime import datetime, timedelta

SCRIPT = "trade_breakout_paper.py"

def sleep_until_next_5min():
    now = datetime.now()
    # prochain multiple de 5 minutes + 5 secondes
    next_min = (now.minute // 5 + 1) * 5
    if next_min >= 60:
        target = (now.replace(minute=0, second=5, microsecond=0) + timedelta(hours=1))
    else:
        target = now.replace(minute=next_min, second=5, microsecond=0)
    dt = (target - now).total_seconds()
    if dt > 0:
        time.sleep(dt)

if __name__ == "__main__":
    while True:
        logger.info('heartbeat: sleeping until next 5m tick')
        sleep_until_next_5min()
        print("\n=== RUN", datetime.now().isoformat(timespec="seconds"), "===")
        subprocess.run([sys.executable, SCRIPT], check=False)
        logger.info('heartbeat: cycle completed')
