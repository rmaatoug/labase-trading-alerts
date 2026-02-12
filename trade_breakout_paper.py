from ib_insync import *
import math
import csv
import json
from datetime import datetime, timezone, date

# --- monitoring / logging ---
from infra.logger import setup_logger
from infra.metrics import load_metrics, inc
import os
logger = setup_logger('logs/bot.log')
metrics = load_metrics()
SHUTTING_DOWN = False
CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', '7'))
IB_HOST = os.getenv('IBKR_HOST', '127.0.0.1')
IB_PORT = int(os.getenv('IBKR_PORT', '7497'))
logger.info('SCRIPT START trade_breakout_paper')
# --- end monitoring ---

# --- Load tickers from configuration ---
try:
    with open('tickers.json', 'r') as f:
        config = json.load(f)
        TICKERS = config.get('tickers', ['AAPL'])
except FileNotFoundError:
    logger.warning("tickers.json not found, using default: AAPL")
    TICKERS = ['AAPL']
# --- end load tickers ---

N = 12
RISK_EUR = 200.0
FX_USD_EUR = 0.92
MAX_POSITION_EUR = 4000

LOG_FILE = "trades_log.csv"
FORCE_TRADE = False
ib = IB()
ib.connect(IB_HOST, IB_PORT, clientId=CLIENT_ID)
logger.info(f"IB_CONNECT host={IB_HOST} port={IB_PORT} clientId={CLIENT_ID}")

# --- IBKR event handlers ---
def on_ib_error(reqId, errorCode, errorString, contract):
    inc('api_errors')
    sym = getattr(contract, 'symbol', None) if contract else None
    logger.error(f'IB_ERROR reqId={reqId} code={errorCode} symbol={sym} msg={errorString}')
    
    # Critical error: notify on disconnect without reconnect
    if errorCode in (1100, 1101, 1102):  # IB disconnect codes
        from infra.notifier import notify, fmt_event
        msg = fmt_event(
            "⚠️ IBKR DISCONNECTED",
            Error=f"Code {errorCode}",
            Message=errorString
        )
        notify(msg)
        logger.critical(f"IBKR disconnect error notified: {errorString}")

def on_ib_disconnected():
    # One-shot script: disconnect at end is normal.
    logger.info('IB_DISCONNECTED')

ib.errorEvent += on_ib_error
ib.disconnectedEvent += on_ib_disconnected
# --- end IBKR event handlers ---

# --- order status tracking ---
def attach_trade_metrics(trade, tag: str):
    # tag example: 'BUY' or 'STOP'
    def _on_status(tr):
        st = getattr(tr.orderStatus, 'status', None)
        filled = getattr(tr.orderStatus, 'filled', None)
        remaining = getattr(tr.orderStatus, 'remaining', None)
        sym = getattr(tr.contract, 'symbol', None) if getattr(tr, 'contract', None) else None
        if st in ('Filled',):
            inc(metrics, 'orders_filled')
            logger.info(f'ORDER_FILLED tag={tag} symbol={sym} filled={filled} remaining={remaining}')
        elif st in ('Cancelled', 'Inactive', 'ApiCancelled'):
            # not necessarily a reject, but useful
            logger.warning(f'ORDER_CANCELLED tag={tag} symbol={sym} status={st} filled={filled} remaining={remaining}')
        elif st in ('Rejected',):
            inc(metrics, 'orders_rejected')
            logger.error(f'ORDER_REJECTED tag={tag} symbol={sym} status={st}')
        else:
            logger.info(f'ORDER_STATUS tag={tag} symbol={sym} status={st} filled={filled} remaining={remaining}')
    try:
        trade.statusEvent += _on_status
    except Exception as e:
        logger.error(f'Could not attach statusEvent: {e}')
        inc('event_attachment_errors')
# --- end order status tracking ---

# --- logging helper ---
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
# --- end logging helper ---

# --- Trading logic for a single symbol ---
def process_ticker(SYMBOL):
    try:
        # Determine currency
        if SYMBOL.endswith('.PA') or SYMBOL.endswith('.AS'):
            # European stocks
            currency = "EUR"
            exchange = "SMART"
        elif SYMBOL in ('BTC-EUR',):
            # Crypto
            currency = "EUR"
            exchange = "SMART"
        else:
            # US stocks
            currency = "USD"
            exchange = "SMART"
        
        contract = Stock(SYMBOL, exchange, currency)
        ib.qualifyContracts(contract)
        
        if not contract.conId:
            logger.warning(f"Could not qualify contract: {SYMBOL}")
            return

        bars = ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr="2 D",
            barSizeSetting="5 mins",
            whatToShow="TRADES",
            useRTH=True,
            formatDate=1
        )

        if not bars or len(bars) <= N:
            logger.warning(f"{SYMBOL}: Not enough bars ({len(bars)})")
            return

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
            if currency == "USD":
                risk_per_share_eur = risk_per_share_usd * FX_USD_EUR
            else:
                risk_per_share_eur = risk_per_share_usd
            qty_risk = math.floor(RISK_EUR / risk_per_share_eur)

            price_eur = entry * (FX_USD_EUR if currency == "USD" else 1.0)
            qty_value = math.floor(MAX_POSITION_EUR / price_eur) if price_eur > 0 else 0

            qty = min(qty_risk, qty_value)
            # Cap at IBKR order limit (500)
            qty = min(qty, 500)

        now = datetime.now(timezone.utc).isoformat()

        print(f"[{SYMBOL}] last={last.date} close={entry} HH={hh} LL={ll} signal={signal} qty={qty}")

        # --- 1 trade par jour par ticker ---
        today_str = datetime.now(timezone.utc).date().isoformat()
        already_traded_today = False

        try:
            with open(LOG_FILE, "r", newline="") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if (
                        r.get("symbol") == SYMBOL and
                        r.get("action") == "ENTER_LONG" and
                        r.get("ts_utc", "").startswith(today_str)
                    ):
                        already_traded_today = True
                        break
        except FileNotFoundError:
            pass

        # --- action ---
        action = "NO_TRADE"
        order_status = ""
        stop_status = ""

        # Blocage si déjà tradé aujourd'hui
        if already_traded_today:
            print(f"{SYMBOL} déjà tradé aujourd'hui -> blocage.")
            signal = False
            FORCE_TRADE = False  # sécurité

        # 1 position max
        positions = ib.positions()
        current_position = next(
            (p for p in positions if p.contract.symbol == SYMBOL),
            None
        )

        if current_position and current_position.position != 0:
            print(f"Déjà en position: {current_position.position} -> pas de nouvelle entrée.")
            signal = False

        if (signal or FORCE_TRADE) and qty > 0:
            action = "ENTER_LONG"

            # Market buy
            buy = MarketOrder("BUY", qty)
            trade_buy = ib.placeOrder(contract, buy)
            
            inc('orders_sent')
            logger.info(f'ORDER_SENT tag=BUY symbol={contract.symbol} qty={qty}')
            attach_trade_metrics(trade_buy, 'BUY')
            ib.sleep(1)
            order_status = trade_buy.orderStatus.status
            print("BUY status:", order_status)

            # Protective stop (avoid duplicates)
            open_trades = ib.trades()
            has_stop = any(
                (t.contract.symbol == SYMBOL
                 and getattr(t.order, "orderType", "") == "STP"
                 and t.orderStatus.status not in ("Cancelled", "Filled"))
                for t in open_trades
            )

            if has_stop:
                print("Stop déjà présent -> je n'en place pas un autre.")
            else:
                stop_order = StopOrder("SELL", qty, stopPrice=stop)
                trade_stop = ib.placeOrder(contract, stop_order)
                
                inc('orders_sent')
                logger.info(f'ORDER_SENT tag=STOP symbol={contract.symbol} qty={qty} stop={stop}')
                attach_trade_metrics(trade_stop, 'STOP')
                ib.sleep(1)
                stop_status = trade_stop.orderStatus.status
                print("STOP status:", stop_status)

        else:
            print(f"[{SYMBOL}] No trade.")

        append_log({
            "ts_utc": now,
            "symbol": SYMBOL,
            "bar_time": str(last.date),
            "close": entry,
            "hh": float(hh),
            "ll": float(ll),
            "signal": signal,
            "qty": qty,
            "stop": stop,
            "action": action,
            "buy_status": order_status,
            "stop_status": stop_status
        })

        # --- Send Telegram notification ---
        from infra.notifier import notify, fmt_event
        
        # Only notify on: signal, trade execution, or errors
        should_notify = signal or action == "ENTER_LONG" or order_status == "Filled" or stop_status == "Filled"
        
        if should_notify:
            msg = fmt_event(
                f"Trade Check: {SYMBOL}",
                Signal=signal,
                Close=f"{entry:.2f}",
                HH=f"{hh:.2f}",
                LL=f"{ll:.2f}",
                Qty=qty,
                Action=action
            )
            if notify(msg):
                logger.info(f"Telegram sent OK for {SYMBOL}")
            else:
                logger.warning(f"Telegram send failed for {SYMBOL}")
        # --- end Telegram notification ---

    except Exception as e:
        logger.error(f"Error processing {SYMBOL}: {e}", exc_info=True)
        inc('api_errors')
# --- end trading logic ---

# --- Main processing loop ---
if __name__ == "__main__":
    try:
        logger.info(f"Processing {len(TICKERS)} tickers")
        for symbol in TICKERS:
            try:
                process_ticker(symbol)
                ib.sleep(0.5)  # Small delay between tickers
            except Exception as e:
                logger.error(f"Failed to process {symbol}: {e}")
                continue
        
        logger.info("All tickers processed successfully")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Disconnect at the very end
        try:
            ib.disconnect()
        except Exception:
            pass
        SHUTTING_DOWN = True
        logger.info("SCRIPT END trade_breakout_paper")
