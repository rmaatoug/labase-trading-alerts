from ib_insync import *
import math

SYMBOL = "AAPL"
N = 12                 # 12 bougies de 5m = 60 minutes
RISK_EUR = 200.0       # risque max par trade
FX_USD_EUR = 0.92      # approx (on fera mieux après)

ib = IB()
ib.connect("127.0.0.1", 7497, clientId=7)

contract = Stock(SYMBOL, "SMART", "USD")
ib.qualifyContracts(contract)

bars = ib.reqHistoricalData(
    contract,
    endDateTime="",
    durationStr="2 D",
    barSizeSetting="5 mins",
    whatToShow="TRADES",
    useRTH=True,
    formatDate=1
)

if len(bars) < N + 1:
    raise SystemExit(f"Pas assez de données: {len(bars)} bars")

# on utilise les N barres précédentes (pas la dernière) pour calculer range
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
    # conversion approx en EUR pour dimensionner le risque
    risk_per_share_eur = risk_per_share_usd * FX_USD_EUR
    qty = math.floor(RISK_EUR / risk_per_share_eur)

print(f"Last bar: {last.date} close={last.close}")
print(f"{N} bars HH={hh} LL={ll}")
print("Signal breakout:", signal)
print(f"Entry={entry} Stop={stop} Risk/share USD={risk_per_share_usd:.4f} -> Qty={qty}")

ib.disconnect()
