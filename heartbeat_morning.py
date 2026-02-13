#!/usr/bin/env python3
"""
Heartbeat matinal - Notification quotidienne de bon fonctionnement
À lancer via cron tous les jours à 9h:
0 9 * * * cd ~/labase-trading-alerts && python3 heartbeat_morning.py
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from src.telegram_client import send_telegram

load_dotenv()

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
