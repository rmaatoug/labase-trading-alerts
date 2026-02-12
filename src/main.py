import os
from dotenv import load_dotenv
from telegram_client import send_telegram
from ibkr_client import connect_ibkr


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
                send_telegram(token, chat_id, "✅ Telegram OK — pipeline V1 prêt.")
                print("Telegram: OK")
            except Exception as e:
                print("Warning: Telegram send failed:", e)
        else:
            print("Telegram: skipped (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")

    host = os.environ["IBKR_HOST"]
    port = int(os.environ["IBKR_PORT"])
    client_id = int(os.environ["IBKR_CLIENT_ID"])

    try:
        ib = connect_ibkr(host, port, client_id)
        if ib.isConnected():
            print("IBKR connected: True")
            ib.disconnect()
        else:
            print("IBKR connected: False (connection not established)")
    except ConnectionRefusedError as e:
        print(f"❌ IBKR connection failed: {e}")
        print(f"   Make sure TWS/IB Gateway is running at {host}:{port} with API access enabled.")
    except OSError as e:
        print(f"❌ Network error connecting to IBKR at {host}:{port}: {e}")


if __name__ == "__main__":
    main()
