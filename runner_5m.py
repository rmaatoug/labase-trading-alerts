# --- AUTO-ADDED: logging + metrics ---

from dotenv import load_dotenv
load_dotenv()
import os
import time
from datetime import datetime, timedelta
from infra.logger import setup_logger
from infra.metrics import load_metrics
from src.telegram_client import send_telegram
import subprocess

logger = setup_logger("logs/bot.log")
metrics = load_metrics()
logger.info("RUNNER START")

SCRIPT = "trade_breakout_paper.py"
DAILY_REPORT_SCRIPT = "daily_report.py"
DAILY_REPORT_HOUR = 22
HEARTBEAT_FILE = "logs/last_heartbeat.txt"
last_report_date = None

def write_heartbeat():
    """Écrit le timestamp actuel pour le watchdog"""
    try:
        os.makedirs("logs", exist_ok=True)
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
    except Exception as e:
        logger.warning(f"Failed to write heartbeat: {e}")

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
        try:
            logger.info('heartbeat: sleeping until next 5m tick')
            sleep_until_next_5min()
            
            # Écrire heartbeat pour watchdog
            write_heartbeat()
            
            print("\n=== RUN", datetime.now().isoformat(timespec="seconds"), "===")
            result = subprocess.run([sys.executable, SCRIPT], check=False)
            
            # Alerter si le script de trading échoue
            if result.returncode != 0:
                logger.error(f"Trading script failed with exit code {result.returncode}")
                try:
                    error_msg = f"❌ ERREUR CRITIQUE\n\n{SCRIPT} a échoué (code {result.returncode})\n\nVérifier logs/bot.log"
                    send_telegram(bot_token, chat_id, error_msg)
                except Exception as e:
                    logger.error(f"Failed to send error notification: {e}")
            
            logger.info('heartbeat: cycle completed')
            
            # Rapport quotidien à 22h (ou juste après)
            now = datetime.now()
            today = now.date()
            if now.hour >= DAILY_REPORT_HOUR and last_report_date != today:
                logger.info(f"Sending daily report for {today}")
                try:
                    subprocess.run([sys.executable, DAILY_REPORT_SCRIPT], check=False)
                    last_report_date = today
                    logger.info("Daily report sent successfully")
                except Exception as e:
                    logger.error(f"Failed to send daily report: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user (Ctrl+C)")
            try:
                stop_msg = f"🛑 Bot arrêté manuellement\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                send_telegram(bot_token, chat_id, stop_msg)
            except:
                pass
            break
            
        except Exception as e:
            logger.error(f"FATAL ERROR in runner loop: {e}", exc_info=True)
            try:
                crash_msg = f"💥 BOT CRASHÉ\n\nErreur fatale: {str(e)}\n\nRedémarrage par watchdog prévu dans 1h max."
                send_telegram(bot_token, chat_id, crash_msg)
            except:
                pass
            # Attendre un peu avant de réessayer (éviter boucle infinie rapide)
            time.sleep(60)
