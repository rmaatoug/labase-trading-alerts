#!/usr/bin/env python3
"""
Heartbeat matinal - Notification quotidienne de bon fonctionnement
À lancer via cron tous les jours à 15h30 (heure FR, 9h30 NY) :
30 15 * * 1-5 cd ~/labase-trading-alerts && python3 heartbeat_morning.py
import pytz
from datetime import datetime, time
"""


import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
try:
    from src.telegram_client import send_telegram
except ImportError:
    from telegram_client import send_telegram

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RUNNER_SCRIPT = "runner_5m.py"


def is_bot_running():
    """Vérifie si runner_5m.py est en cours d'exécution"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", RUNNER_SCRIPT],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except Exception:
        return False


def get_uptime():
    """Récupère l'uptime du MacBook"""
    try:
        result = subprocess.run(
            ["uptime"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip() if result.returncode == 0 else "N/A"
    except Exception:
        return "N/A"


def count_today_logs():
    """Compte les lignes dans bot.log d'aujourd'hui"""
    try:
        log_file = Path("logs/bot.log")
        if not log_file.exists():
            return 0
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        with open(log_file, 'r') as f:
            count = sum(1 for line in f if today_str in line)
        return count
    except Exception:
        return 0


def main():
    # Vérifie si on est bien pendant l'ouverture du marché US (9h30-16h NY, jours ouvrés)
    ny_tz = pytz.timezone('America/New_York')
    now_ny = datetime.now(ny_tz)
    is_weekday = now_ny.weekday() < 5
    market_open = time(9, 30)
    market_close = time(16, 0)
    if not (is_weekday and market_open <= now_ny.time() <= market_close):
        print("Marché US fermé, pas d'envoi Telegram.")
        return
    print(f"🌅 Heartbeat matinal - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    bot_running = is_bot_running()
    uptime = get_uptime()
    log_lines = count_today_logs()
    
    # Message
    if bot_running:
        status_icon = "✅"
        status_text = "Bot ACTIF"
    else:
        status_icon = "❌"
        status_text = "Bot ARRÊTÉ"
    
    msg = f"{status_icon} **BONJOUR - Status quotidien**\n\n"
    msg += f"📅 {datetime.now().strftime('%A %d %B %Y')}\n"
    msg += f"🤖 {status_text}\n"
    msg += f"📊 Logs aujourd'hui: {log_lines} lignes\n"
    msg += f"⏱️ Uptime: {uptime}\n\n"
    
    if bot_running:
        msg += "✅ Tout fonctionne normalement"
    else:
        msg += "⚠️ ATTENTION: Bot non actif !"
    
    try:
        send_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
        print("✅ Heartbeat envoyé sur Telegram")
    except Exception as e:
        print(f"❌ Erreur envoi Telegram: {e}")


if __name__ == "__main__":
    main()
