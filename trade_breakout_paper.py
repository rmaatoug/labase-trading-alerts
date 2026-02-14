import math
import csv
import json
from datetime import datetime, timezone, date
import time

# --- monitoring / logging ---
from infra.logger import setup_logger
from infra.metrics import load_metrics, inc
import os

logger = setup_logger('logs/bot.log')
metrics = load_metrics()
SHUTTING_DOWN = False

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

# --- Connect to Alpaca ---
from src.alpaca_client import connect_alpaca
from infra.notifier import notify, fmt_event

try:
    alpaca = connect_alpaca()
    logger.info("ALPACA_CONNECT success")
except Exception as e:
    logger.error(f"ALPACA_CONNECT failed: {e}")
    # Send Telegram alert
    try:
        error_msg = fmt_event(
            "❌ ERREUR ALPACA CONNEXION",
            Erreur=str(e),
            Action="Vérifier API keys et réseau"
        )
        notify(error_msg)
    except:
        pass
    exit(1)
# --- end Alpaca connection ---

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
        FORCE_TRADE = False  # Initialize local variable
        
        # Alpaca only supports US stocks
        currency = "USD"
        
        # Get historical bars (2 days of 5-min data)
        try:
            bars = alpaca.get_historical_bars(SYMBOL, days=2, timeframe='5Min')
        except Exception as e:
            logger.error(f"{SYMBOL}: Failed to fetch bars: {e}")
            error_msg = fmt_event(
                f"❌ ERREUR API ALPACA - {SYMBOL}",
                Erreur="Impossible de récupérer les données historiques",
                Details=str(e)
            )
            notify(error_msg)
            return

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
            risk_per_share_eur = risk_per_share_usd * FX_USD_EUR
            qty_risk = math.floor(RISK_EUR / risk_per_share_eur)

            price_eur = entry * FX_USD_EUR
            qty_value = math.floor(MAX_POSITION_EUR / price_eur) if price_eur > 0 else 0

            qty = min(qty_risk, qty_value)
            # Cap at 500 for safety
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
        try:
            positions = alpaca.get_positions()
            current_position = next(
                (p for p in positions if p.symbol == SYMBOL),
                None
            )
        except Exception as e:
            logger.error(f"{SYMBOL}: Failed to fetch positions: {e}")
            error_msg = fmt_event(
                f"❌ ERREUR API ALPACA - {SYMBOL}",
                Erreur="Impossible de récupérer les positions",
                Details=str(e)
            )
            notify(error_msg)
            return

        if current_position and float(current_position.qty) != 0:
            print(f"Déjà en position: {current_position.qty} -> pas de nouvelle entrée.")
            signal = False

        if (signal or FORCE_TRADE) and qty > 0:
            action = "ENTER_LONG"

            # Market buy
            try:
                buy_order = alpaca.place_market_order(SYMBOL, qty, side='buy')
            except Exception as e:
                logger.error(f"{SYMBOL}: Failed to place buy order: {e}")
                error_msg = fmt_event(
                    f"❌ ERREUR PLACEMENT ORDRE - {SYMBOL}",
                    Type="Market BUY",
                    Qty=qty,
                    Erreur=str(e)
                )
                notify(error_msg)
                inc('orders_rejected')
                return
            
            if buy_order:
                inc('orders_sent')
                logger.info(f'ORDER_SENT tag=BUY symbol={SYMBOL} qty={qty}')
                
                # Wait a bit for order to fill
                time.sleep(2)
                
                # Check order status
                try:
                    orders = alpaca.get_orders(status='all')
                    buy_order_updated = next((o for o in orders if o.id == buy_order.id), buy_order)
                    order_status = buy_order_updated.status
                    print("BUY status:", order_status)
                    
                    if order_status in ('filled', 'FILLED'):
                        inc('orders_filled')
                except Exception as e:
                    logger.error(f"{SYMBOL}: Failed to check order status: {e}")
                    order_status = "UNKNOWN"

                # Protective stop
                # Check if stop already exists
                try:
                    open_orders = alpaca.get_orders(status='open')
                    has_stop = any(
                        (o.symbol == SYMBOL and 
                         hasattr(o, 'stop_price') and 
                         o.stop_price is not None)
                        for o in open_orders
                    )
                except Exception as e:
                    logger.error(f"{SYMBOL}: Failed to check open orders: {e}")
                    has_stop = False

                if has_stop:
                    print("Stop déjà présent -> je n'en place pas un autre.")
                else:
                    try:
                        stop_order = alpaca.place_stop_order(SYMBOL, qty, stop_price=stop, side='sell')
                        
                        if stop_order:
                            inc('orders_sent')
                            logger.info(f'ORDER_SENT tag=STOP symbol={SYMBOL} qty={qty} stop={stop}')
                            
                            time.sleep(1)
                            
                            # Check stop status
                            try:
                                orders = alpaca.get_orders(status='all')
                                stop_order_updated = next((o for o in orders if o.id == stop_order.id), stop_order)
                                stop_status = stop_order_updated.status
                                print("STOP status:", stop_status)
                            except Exception as e:
                                logger.error(f"{SYMBOL}: Failed to check stop order status: {e}")
                                stop_status = "UNKNOWN"
                    except Exception as e:
                        logger.error(f"{SYMBOL}: Failed to place stop order: {e}")
                        error_msg = fmt_event(
                            f"⚠️ ERREUR STOP LOSS - {SYMBOL}",
                            Type="Stop Order",
                            Qty=qty,
                            StopPrice=f"{stop:.2f}",
                            Erreur=str(e),
                            Warning="Position non protégée!"
                        )
                        notify(error_msg)
                        inc('orders_rejected')
            else:
                logger.error(f"Failed to place buy order for {SYMBOL}")
                error_msg = fmt_event(
                    f"❌ ERREUR ORDRE BUY - {SYMBOL}",
                    Qty=qty,
                    Erreur="Buy order returned None"
                )
                notify(error_msg)
                inc('orders_rejected')

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
        should_notify = signal or action == "ENTER_LONG" or order_status in ('filled', 'FILLED') or stop_status in ('filled', 'FILLED')
        
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
        # Send Telegram alert for unexpected errors
        try:
            error_msg = fmt_event(
                f"❌ ERREUR INATTENDUE - {SYMBOL}",
                Erreur=str(e)[:200],  # Limit error message length
                Action="Vérifier logs/bot.log"
            )
            notify(error_msg)
        except:
            pass
# --- end trading logic ---

# --- Main processing loop ---
if __name__ == "__main__":
    try:
        logger.info(f"Processing {len(TICKERS)} tickers")
        for symbol in TICKERS:
            try:
                process_ticker(symbol)
                time.sleep(0.5)  # Small delay between tickers
            except Exception as e:
                logger.error(f"Failed to process {symbol}: {e}")
                continue
        
        logger.info("All tickers processed successfully")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        # Send Telegram alert for fatal errors
        try:
            error_msg = fmt_event(
                "💥 ERREUR FATALE BOT",
                Erreur=str(e)[:200],
                Action="Vérifier logs/bot.log immédiatement"
            )
            notify(error_msg)
        except:
            pass
    finally:
        # Disconnect at the very end
        try:
            alpaca.disconnect()
        except Exception:
            pass
        SHUTTING_DOWN = True
        logger.info("SCRIPT END trade_breakout_paper")
