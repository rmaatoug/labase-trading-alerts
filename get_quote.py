import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
BASE_URL = 'https://data.alpaca.markets/v2/stocks/quotes/latest'

def get_quote(symbol):
    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY
    }
    params = {'symbols': symbol}
    r = requests.get(BASE_URL, headers=headers, params=params)
    r.raise_for_status()
    data = r.json()
    try:
        quote = data['quotes'][symbol]
        ask = quote['ap']
        bid = quote['bp']
        t = quote['t']
        print(f"{symbol} ask: {ask} | bid: {bid} | time: {t}")
    except Exception as e:
        print(f"Erreur ou données manquantes pour {symbol}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_quote.py TICKER")
        sys.exit(1)
    symbol = sys.argv[1].upper()
    get_quote(symbol)