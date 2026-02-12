from ib_insync import *
import math
import csv
from datetime import datetime, timezone

SYMBOLS = ["AAPL", "NVDA", "TSLA", "QQQ"]   # ajoute/retire ici
N = 12                                     # 12*5min = 60 minutes
RISK_EUR = 200.0
FX_USD_EUR = 0.92                          # approx
MAX_POSITION_EUR = 4000

LOG_FILE = "trades_log.csv"
FORCE_TRADE = False                         # garde False

def append_log(row: dict):
    file_exists = False
    try:
        with open(LOG_FILE, "r", newline="") as _:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def already_traded_today(symbol: str) -> bool:
    today_str = datetime.now(timezone.utc).date().isoformat()
    try:
        with open(LOG_FILE, "r", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                if (
                    r.get("symbol") == symbol and
                    r.get("action") == "ENTER_LONG" and
                    r.get("ts_utc", "").startswith(today_str)
                ):
                    return True
    except FileNotFoundError:
        return False
    return False

ib = IB()
ib.connect("127.0.0.1", 7497, clientId=9)

positions = {p.contract.symbol: p.position for p in ib.positions()}

for symbol in SYMBOLS:
    contract = Stock(symbol, "SMART", "USD")
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
        print(f"[{symbol}] pas assez de bars ({len(bars)}) -> skip")
        continue

    window = bars[-(N+1):-1]
    last = bars[-1]

    hh = max(b.high for b in window)
    ll = min(b.low for b in window)

    entry = float(last.close)
    stop = float(ll)

    signal = entry > hh
    risk_per_share_usd = max(entry - stop, 0.0)

    qty = 0
    if risk_per_share_usd > 0:
        risk_per_share_eur = risk_per_share_usd * FX_USD_EUR
        qty_risk = math.floor(RISK_EUR / risk_per_share_eur)

        price_eur = entry * FX_USD_EUR
        qty_value = math.floor(MAX_POSITION_EUR / price_eur)

        qty = max(0, min(qty_risk, qty_value))

    now = datetime.now(timezone.utc).isoformat()
    action = "NO_TRADE"
    buy_status = ""
    stop_status = ""

    print(f"[{symbol}] close={entry} HH={hh} LL={ll} signal={signal} qty={qty}")

    # --- Guards: 1 trade/day per symbol + 1 position max per symbol ---
    if already_traded_today(symbol):
        print(f"[{symbol}] déjà tradé aujourd’hui -> blocage")
        signal = False

    if positions.get(symbol, 0) != 0:
        print(f"[{symbol}] déjà en position {positions[symbol]} -> blocage")
        signal = False

    if (signal or FORCE_TRADE) and qty > 0:
        action = "ENTER_LONG"

        buy = MarketOrder("BUY", qty)
        trade_buy = ib.placeOrder(contract, buy)
        ib.sleep(2)
        buy_status = trade_buy.orderStatus.status
        print(f"[{symbol}] BUY status:", buy_status)

        # Protective stop (avoid duplicates)
        open_trades = ib.trades()
        has_stop = any(
            (t.contract.symbol == symbol
             and getattr(t.order, "orderType", "") == "STP"
             and t.orderStatus.status not in ("Cancelled", "Filled"))
            for t in open_trades
        )

        if has_stop:
            print(f"[{symbol}] stop déjà présent -> pas de doublon")
        else:
            stp = StopOrder("SELL", qty, stopPrice=stop)
            trade_stop = ib.placeOrder(contract, stp)
            ib.sleep(2)
            stop_status = trade_stop.orderStatus.status
            print(f"[{symbol}] STOP status:", stop_status)
    else:
        print(f"[{symbol}] No trade.")

    # --- calcul exposition ---
    position_value_eur = qty * entry * FX_USD_EUR

    append_log({
        "ts_utc": now,
        "symbol": symbol,
        "bar_time": str(last.date),
        "close": entry,
        "hh": float(hh),
        "ll": float(ll),
        "signal": signal,
        "qty": qty,
        "stop": stop,
        "risk_per_share_usd": round(risk_per_share_usd, 4),
        "position_value_eur": round(position_value_eur, 2),
        "action": action,
        "buy_status": buy_status,
        "stop_status": stop_status
    })

ib.disconnect()
