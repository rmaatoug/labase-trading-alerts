#!/usr/bin/env python3
"""
Rapport quotidien de trading - envoyé sur Telegram
Lance ce script en fin de journée (ex: 22h via cron)
Sauvegarde aussi les performances dans performance_log.csv
"""

from ib_insync import IB
import csv
import os
from datetime import datetime, timezone, date
from dotenv import load_dotenv
from src.telegram_client import send_telegram
from infra.logger import setup_logger
from infra.summary import (
    calculate_win_rate,
    calculate_pnl,
    save_daily_performance,
    load_performance_history,
    calculate_sharpe_ratio,
    calculate_max_drawdown
)

load_dotenv()
logger = setup_logger("logs/bot.log")

# Configuration
LOG_FILE = "trades_log.csv"
CLIENT_ID = int(os.getenv('IBKR_CLIENT_ID', '9'))  # Différent des autres scripts
IB_HOST = os.getenv('IBKR_HOST', '127.0.0.1')
IB_PORT = int(os.getenv('IBKR_PORT', '7497'))
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def read_today_trades():
    """Lit les trades du jour depuis trades_log.csv"""
    today_str = date.today().isoformat()
    trades = []
    
    try:
        with open(LOG_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Format: 2026-02-13T10:35:42.123456+00:00
                ts = row.get('ts_utc', '')
                if ts.startswith(today_str):
                    trades.append(row)
    except FileNotFoundError:
        logger.warning(f"{LOG_FILE} not found")
    
    return trades


def get_account_info():
    """Récupère les infos du compte IBKR"""
    ib = IB()
    try:
        ib.connect(IB_HOST, IB_PORT, clientId=CLIENT_ID)
        
        # Capital
        net_liq = 0
        available = 0
        for item in ib.accountSummary():
            if item.tag == "NetLiquidation" and item.currency == "USD":
                net_liq = float(item.value)
            if item.tag == "AvailableFunds" and item.currency == "USD":
                available = float(item.value)
        
        # Positions ouvertes
        positions = ib.positions()
        open_positions = [(p.contract.symbol, int(p.position), round(p.avgCost, 2)) 
                          for p in positions if p.position != 0]
        
        ib.disconnect()
        return net_liq, available, open_positions
    
    except Exception as e:
        logger.error(f"Failed to get IBKR account info: {e}")
        return 0, 0, []


def generate_report():
    """Génère le rapport quotidien et sauvegarde les performances"""
    today = date.today()
    today_trades = read_today_trades()
    net_liq, available, positions = get_account_info()
    
    # Stats du jour
    signals = [t for t in today_trades if t.get('signal') == 'True']
    entries = [t for t in today_trades if t.get('action') == 'ENTER_LONG']
    stops_filled = [t for t in today_trades if t.get('stop_status') == 'Filled']
    
    # Calculs de performance
    win_rate = calculate_win_rate(today_trades)
    pnl = calculate_pnl(today_trades)
    
    # Sauvegarder les performances quotidiennes
    try:
        save_daily_performance(
            day=today,
            net_liq=net_liq,
            available=available,
            signals=len(signals),
            entries=len(entries),
            stops_filled=len(stops_filled),
            open_positions=len(positions),
            win_rate=win_rate,
            pnl=pnl
        )
        logger.info(f"Daily performance saved: net_liq={net_liq}, pnl={pnl}")
    except Exception as e:
        logger.error(f"Failed to save daily performance: {e}")
    
    # Métriques historiques (30 derniers jours)
    history = load_performance_history(days=30)
    sharpe = calculate_sharpe_ratio(history) if len(history) >= 2 else 0.0
    max_dd = calculate_max_drawdown(history) if history else 0.0
    
    # Formatage message Telegram
    msg = f"📊 **RAPPORT QUOTIDIEN** - {today.strftime('%d/%m/%Y')}\n\n"
    
    msg += f"💰 **Capital**\n"
    msg += f"  • Net Liquidation: ${net_liq:,.0f}\n"
    msg += f"  • Disponible: ${available:,.0f}\n\n"
    
    msg += f"📈 **Activité du jour**\n"
    msg += f"  • Signaux détectés: {len(signals)}\n"
    msg += f"  • Ordres passés: {len(entries)}\n"
    msg += f"  • Stops remplis: {len(stops_filled)}\n"
    if stops_filled:
        msg += f"  • Win rate: {win_rate:.1f}%\n"
        msg += f"  • P&L: ${pnl:,.2f}\n"
    msg += "\n"
    
    if positions:
        msg += f"📦 **Positions ouvertes** ({len(positions)})\n"
        for symbol, qty, avg_cost in positions[:10]:  # Max 10 positions
            msg += f"  • {symbol}: {qty} @ ${avg_cost}\n"
        if len(positions) > 10:
            msg += f"  • ... et {len(positions) - 10} autres\n"
    else:
        msg += f"📦 **Positions ouvertes**: Aucune\n"
    
    # Métriques sur 30 jours
    if len(history) >= 2:
        msg += f"\n📊 **Performance 30j**\n"
        msg += f"  • Sharpe Ratio: {sharpe:.2f}\n"
        msg += f"  • Max Drawdown: {max_dd:.2f}%\n"
    
    msg += f"\n✅ Trading terminé pour aujourd'hui"
    
    return msg


def main():
    logger.info("DAILY_REPORT START")
    
    try:
        report = generate_report()
        send_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, report)
        logger.info("Daily report sent successfully")
        print("✅ Rapport envoyé sur Telegram")
    
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()
