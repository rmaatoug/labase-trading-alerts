"""Trade summary and performance analytics."""

import csv
from datetime import date
from typing import List, Dict, Optional


PERFORMANCE_LOG = "performance_log.csv"


def calculate_win_rate(trades: List[Dict]) -> float:
    """Calcule le win rate (% de stops profitable)."""
    filled_stops = [t for t in trades if t.get('stop_status') == 'Filled']
    if not filled_stops:
        return 0.0
    
    wins = 0
    for trade in filled_stops:
        try:
            entry = float(trade.get('entry', 0))
            stop = float(trade.get('stop', 0))
            # Si stop > entry, c'est un gain (on est long)
            if stop > entry:
                wins += 1
        except (ValueError, TypeError):
            continue
    
    return (wins / len(filled_stops)) * 100 if filled_stops else 0.0


def calculate_pnl(trades: List[Dict]) -> float:
    """Calcule le P&L approximatif des trades fermés."""
    pnl = 0.0
    for trade in trades:
        if trade.get('stop_status') != 'Filled':
            continue
        try:
            entry = float(trade.get('entry', 0))
            stop = float(trade.get('stop', 0))
            qty = int(trade.get('qty', 0))
            pnl += (stop - entry) * qty
        except (ValueError, TypeError):
            continue
    return pnl


def save_daily_performance(
    day: date,
    net_liq: float,
    available: float,
    signals: int,
    entries: int,
    stops_filled: int,
    open_positions: int,
    win_rate: float,
    pnl: float
) -> None:
    """Sauvegarde les performances quotidiennes dans performance_log.csv"""
    
    # Créer le fichier avec header si inexistant
    try:
        with open(PERFORMANCE_LOG, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'date', 'net_liquidation', 'available_funds', 
                'signals', 'entries', 'stops_filled', 'open_positions',
                'win_rate_pct', 'pnl_usd'
            ])
    except FileExistsError:
        pass
    
    # Ajouter la ligne du jour
    with open(PERFORMANCE_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            day.isoformat(),
            round(net_liq, 2),
            round(available, 2),
            signals,
            entries,
            stops_filled,
            open_positions,
            round(win_rate, 2),
            round(pnl, 2)
        ])


def load_performance_history(days: Optional[int] = None) -> List[Dict]:
    """Charge l'historique des performances.
    
    Args:
        days: Nombre de jours à charger (None = tout)
    
    Returns:
        Liste de dicts avec les performances quotidiennes
    """
    try:
        with open(PERFORMANCE_LOG, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if days:
                return rows[-days:]
            return rows
    except FileNotFoundError:
        return []


def calculate_sharpe_ratio(history: List[Dict]) -> float:
    """Calcule le ratio de Sharpe approximatif (annualisé).
    
    Simplifié : rendement moyen / volatilité
    """
    if len(history) < 2:
        return 0.0
    
    returns = []
    for i in range(1, len(history)):
        prev = float(history[i-1].get('net_liquidation', 0))
        curr = float(history[i].get('net_liquidation', 0))
        if prev > 0:
            ret = (curr - prev) / prev
            returns.append(ret)
    
    if not returns:
        return 0.0
    
    avg_return = sum(returns) / len(returns)
    variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
    std_dev = variance ** 0.5
    
    if std_dev == 0:
        return 0.0
    
    # Annualiser (252 jours de trading par an)
    sharpe = (avg_return / std_dev) * (252 ** 0.5)
    return sharpe


def calculate_max_drawdown(history: List[Dict]) -> float:
    """Calcule le drawdown maximum (%)."""
    if not history:
        return 0.0
    
    peak = 0.0
    max_dd = 0.0
    
    for row in history:
        value = float(row.get('net_liquidation', 0))
        if value > peak:
            peak = value
        
        if peak > 0:
            dd = ((peak - value) / peak) * 100
            if dd > max_dd:
                max_dd = dd
    
    return max_dd


__all__ = [
    "calculate_win_rate",
    "calculate_pnl",
    "save_daily_performance",
    "load_performance_history",
    "calculate_sharpe_ratio",
    "calculate_max_drawdown"
]
