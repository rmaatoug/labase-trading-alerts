#!/usr/bin/env python3
"""
Test accès US Market Data (SIP) via Alpaca
Affiche si la récupération de données SIP fonctionne réellement.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from dotenv import load_dotenv
try:
    from alpaca_client import AlpacaClient
except ImportError:
    from src.alpaca_client import AlpacaClient

load_dotenv()

symbol = "AAPL"
print(f"Test SIP pour {symbol}...")

os.environ["ALPACA_FEED"] = "sip"
client = AlpacaClient()
try:
    bars = client.get_historical_bars(symbol, days=1, timeframe="5Min")
    if bars and len(bars) > 0:
        print(f"✅ Accès US Market Data (SIP) OK : {len(bars)} bars reçues.")
    else:
        print("❌ Pas de données SIP reçues (vérifier abonnement ou droits API).")
except Exception as e:
    print(f"❌ Erreur accès SIP : {e}")
