#!/usr/bin/env python3
"""
Watchdog - Surveillance et redémarrage automatique du bot
À lancer via cron toutes les heures:
0 * * * * cd ~/labase-trading-alerts && python3 watchdog.py
"""


import os
from dotenv import load_dotenv
load_dotenv()
try:
    from src.telegram_client import send_telegram
except ImportError:
    from telegram_client import send_telegram

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RUNNER_SCRIPT = "runner_5m.py"
LAST_HEARTBEAT_FILE = "logs/last_heartbeat.txt"
MAX_HOURS_WITHOUT_HEARTBEAT = 2


def is_bot_running():
    """Vérifie si runner_5m.py est en cours d'exécution"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", RUNNER_SCRIPT],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except Exception as e:
        print(f"❌ Erreur vérification process: {e}")
        return False


def check_last_heartbeat():
    """Vérifie le dernier heartbeat du bot"""
    heartbeat_file = Path(LAST_HEARTBEAT_FILE)
    
    if not heartbeat_file.exists():
        return None
    
    try:
        with open(heartbeat_file, 'r') as f:
            last_time_str = f.read().strip()
            last_time = datetime.fromisoformat(last_time_str)
            return last_time
    except Exception as e:
        print(f"⚠️  Erreur lecture heartbeat: {e}")
        return None


def start_bot():
    """Démarre le bot"""
    try:
        print(f"🚀 Démarrage de {RUNNER_SCRIPT}...")
        subprocess.Popen(
            [sys.executable, RUNNER_SCRIPT],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except Exception as e:
        print(f"❌ Erreur démarrage bot: {e}")
        return False


def send_alert(message):
    """Envoie une alerte Telegram"""
    try:
        full_msg = f"⚠️ WATCHDOG ALERT ⚠️\n\n{message}\n\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, full_msg)
        print(f"📱 Alerte envoyée: {message}")
    except Exception as e:
        print(f"❌ Erreur envoi alerte: {e}")


def main():
    print(f"\n{'='*60}")
    print(f"🔍 WATCHDOG - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    running = is_bot_running()
    print(f"Status bot: {'✅ EN COURS' if running else '❌ ARRÊTÉ'}")
    
    if not running:
        send_alert(f"Bot arrêté détecté !\nTentative de redémarrage automatique...")
        
        if start_bot():
            send_alert("✅ Bot redémarré avec succès")
            print("✅ Bot redémarré")
        else:
            send_alert("❌ ÉCHEC redémarrage bot !\nIntervention manuelle requise.")
            print("❌ Échec redémarrage")
            sys.exit(1)
    else:
        # Vérifier le heartbeat
        last_heartbeat = check_last_heartbeat()
        if last_heartbeat:
            hours_since = (datetime.now() - last_heartbeat).total_seconds() / 3600
            print(f"Dernier heartbeat: il y a {hours_since:.1f}h")
            
            if hours_since > MAX_HOURS_WITHOUT_HEARTBEAT:
                send_alert(f"⏰ Pas de heartbeat depuis {hours_since:.1f}h !\nBot peut être bloqué.")
        else:
            print("⚠️  Pas de fichier heartbeat")
    
    print("\n✅ Watchdog terminé\n")


if __name__ == "__main__":
    main()
