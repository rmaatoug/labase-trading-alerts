import os
from dotenv import load_dotenv
from telegram_client import send_telegram
from ibkr_client import connect_ibkr

def main():
    load_dotenv()

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    send_telegram(token, chat_id, "✅ Telegram OK — pipeline V1 prêt.")
    print("Telegram: OK")

    host = os.environ["IBKR_HOST"]
    port = int(os.environ["IBKR_PORT"])
    client_id = int(os.environ["IBKR_CLIENT_ID"])

    ib = connect_ibkr(host, port, client_id)
    print("IBKR connected:", ib.isConnected())
    ib.disconnect()

if __name__ == "__main__":
    main()
