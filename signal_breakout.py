
# Chargement automatique des variables d'environnement
from dotenv import load_dotenv
load_dotenv()
alpaca = connect_alpaca()
bars = alpaca.get_historical_bars(SYMBOL, days=2, timeframe='5Min')
hh = max(b.high for b in window)
signal = entry > hh

from dotenv import load_dotenv
load_dotenv()
from src.alpaca_client import connect_alpaca
import math

SYMBOL = "AAPL"
N = 12
RISK_EUR = 200.0
FX_USD_EUR = 0.92

alpaca = connect_alpaca()
bars = alpaca.get_historical_bars(SYMBOL, days=2, timeframe='5Min')
if len(bars) < N + 1:
    raise SystemExit(f"Pas assez de données: {len(bars)} bars")
window = bars[-(N+1):-1]
last = bars[-1]
hh = max(b.high for b in window)
ll = min(b.low for b in window)
entry = last.close
stop = ll
signal = entry > hh
risk_per_share_usd = max(entry - stop, 0)
if risk_per_share_usd == 0:
    qty = 0
else:
    risk_per_share_eur = risk_per_share_usd * FX_USD_EUR
    qty = math.floor(RISK_EUR / risk_per_share_eur)
print(f"Last bar: {last.date} close={last.close}")
print(f"{N} bars HH={hh} LL={ll}")
print("Signal breakout:", signal)
print(f"Entry={entry} Stop={stop} Risk/share USD={risk_per_share_usd:.4f} -> Qty={qty}")

ib.disconnect()
