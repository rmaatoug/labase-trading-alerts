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
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.telegram_client import send_telegram

load_dotenv()

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
    # Notification de démarrage
    try:
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        startup_msg = f"🚀 Bot démarré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ runner_5m.py actif"
        send_telegram(bot_token, chat_id, startup_msg)
        logger.info("Startup notification sent to Telegram")
    except Exception as e:
        logger.warning(f"Failed to send startup notification: {e}")
    
    while True:
        logger.info('heartbeat: sleeping until next 5m tick')
        sleep_until_next_5min()
        print("\n=== RUN", datetime.now().isoformat(timespec="seconds"), "===")
        subprocess.run([sys.executable, SCRIPT], check=False)
        logger.info('heartbeat: cycle completed')
