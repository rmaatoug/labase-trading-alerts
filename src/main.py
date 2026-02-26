import os
import sys
from dotenv import load_dotenv

# Ajoute la racine du projet au PYTHONPATH si besoin
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.telegram_client import send_telegram
except ImportError:
    from telegram_client import send_telegram
try:
    from src.alpaca_client import connect_alpaca
except ImportError:
    from alpaca_client import connect_alpaca


def main():
    load_dotenv()

    # Allow skipping Telegram during local tests by setting SKIP_TELEGRAM=1
    skip_telegram = os.environ.get("SKIP_TELEGRAM", "0") in ("1", "true", "True")
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if skip_telegram:
        print("Telegram: skipped (SKIP_TELEGRAM=1)")
    else:
        if token and chat_id:
            try:
                send_telegram(token, chat_id, "✅ Telegram OK — Alpaca bot ready.")
                print("Telegram: OK")
            except Exception as e:
                print("Warning: Telegram send failed:", e)
        else:
            print("Telegram: skipped (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")

    # Test Alpaca connection
    try:
        alpaca = connect_alpaca()
        if alpaca.connected:
            print("Alpaca connected: True")
            account = alpaca.get_account()
            if account:
                print(f"Account equity: ${account.equity:.2f}")
                print(f"Buying power: ${account.buying_power:.2f}")
            alpaca.disconnect()
        else:
            print("Alpaca connected: False (connection not established)")
    except Exception as e:
        print(f"❌ Alpaca connection failed: {e}")
        print(f"   Make sure ALPACA_API_KEY and ALPACA_SECRET_KEY are set in .env")


if __name__ == "__main__":
    main()
