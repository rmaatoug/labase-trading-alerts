#!/usr/bin/env python3
"""
Analyse de performance avec synchronisation automatique
Usage sur Codespaces après avoir copié les fichiers du MacBook:
  1. Sur MacBook: python3 sync_logs.py --backup && git push
  2. Sur Codespaces: git pull && python3 analyze_synced.py --latest
"""

import argparse
import os
from pathlib import Path
from infra.summary import (
    load_performance_history,
    calculate_sharpe_ratio,
    calculate_max_drawdown
)
import csv


def find_latest_backup():
    """Trouve le backup le plus récent dans backups/"""
    backup_dir = Path("backups")
    if not backup_dir.exists():
        return None
    
    subdirs = [d for d in backup_dir.iterdir() if d.is_dir()]
    if not subdirs:
        return None
    
    # Trier par nom (timestamp) décroissant
    latest = sorted(subdirs, reverse=True)[0]
    return latest


def analyze_from_path(perf_log_path, trades_log_path):
    """Analyse les performances depuis des fichiers spécifiques"""
    
    if not Path(perf_log_path).exists():
        print(f"❌ Fichier introuvable: {perf_log_path}")
        print("\n💡 Pour analyser depuis Codespaces:")
        print("   1. Sur MacBook: python3 sync_logs.py --backup")
        print("   2. Sur MacBook: git add backups/ && git commit -m 'backup logs' && git push")
        print("   3. Sur Codespaces: git pull")
        print("   4. Sur Codespaces: python3 analyze_synced.py --latest")
        return
    
    print(f"\n📂 Analyse depuis: {perf_log_path}\n")
    print("=" * 60)
    
    # Lire performance_log.csv
    history = []
    with open(perf_log_path, 'r') as f:
        reader = csv.DictReader(f)
        history = list(reader)
    
    if not history:
        print("❌ Aucune donnée dans performance_log.csv")
        return
    
    # Capital
    first = history[0]
    last = history[-1]
    start_capital = float(first.get('net_liquidation', 0))
    end_capital = float(last.get('net_liquidation', 0))
    pnl_total = end_capital - start_capital
    pnl_pct = (pnl_total / start_capital * 100) if start_capital > 0 else 0
    
    print(f"\n💰 CAPITAL ({len(history)} jours)")
    print(f"  Période:         {first.get('date')} → {last.get('date')}")
    print(f"  Début:           ${start_capital:,.2f}")
    print(f"  Fin:             ${end_capital:,.2f}")
    print(f"  P&L:             ${pnl_total:,.2f} ({pnl_pct:+.2f}%)")
    
    # Activité
    total_signals = sum(int(h.get('signals', 0)) for h in history)
    total_entries = sum(int(h.get('entries', 0)) for h in history)
    total_stops = sum(int(h.get('stops_filled', 0)) for h in history)
    
    print(f"\n📈 ACTIVITÉ")
    print(f"  Signaux détectés:   {total_signals}")
    print(f"  Ordres passés:      {total_entries}")
    print(f"  Stops remplis:      {total_stops}")
    
    if total_signals > 0:
        signal_to_trade = (total_entries / total_signals * 100)
        print(f"  Taux d'exécution:   {signal_to_trade:.1f}%")
    
    # Win rate moyen
    win_rates = [float(h.get('win_rate_pct', 0)) for h in history if float(h.get('win_rate_pct', 0)) > 0]
    if win_rates:
        avg_win_rate = sum(win_rates) / len(win_rates)
        print(f"  Win rate moyen:     {avg_win_rate:.1f}%")
    
    # Métriques de risque
    if len(history) >= 2:
        sharpe = calculate_sharpe_ratio(history)
        max_dd = calculate_max_drawdown(history)
        
        print(f"\n⚠️  RISQUE")
        print(f"  Sharpe Ratio:       {sharpe:.2f}")
        print(f"  Max Drawdown:       {max_dd:.2f}%")
        
        # Interprétation
        print(f"\n💡 INTERPRÉTATION")
        if sharpe > 2:
            print(f"  ✅ Excellent Sharpe (>2) - stratégie très performante")
        elif sharpe > 1:
            print(f"  ✅ Bon Sharpe (>1) - stratégie rentable")
        elif sharpe > 0:
            print(f"  ⚠️  Sharpe positif mais faible - à surveiller")
        else:
            print(f"  ❌ Sharpe négatif - stratégie perdante")
        
        if max_dd < 10:
            print(f"  ✅ Drawdown faible (<10%) - risque maîtrisé")
        elif max_dd < 20:
            print(f"  ⚠️  Drawdown moyen (10-20%) - acceptable")
        else:
            print(f"  ❌ Drawdown élevé (>20%) - risque important")
    
    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Analyse de performance depuis fichiers synchronisés"
    )
    parser.add_argument(
        '--latest',
        action='store_true',
        help='Analyser le dernier backup dans backups/'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help='Analyser depuis data/ (local uniquement)'
    )
    parser.add_argument(
        '--backup',
        type=str,
        help='Analyser un backup spécifique (ex: backups/20260213_220000)'
    )
    
    args = parser.parse_args()
    
    if args.latest:
        latest = find_latest_backup()
        if not latest:
            print("❌ Aucun backup trouvé dans backups/")
            print("\n💡 Créer un backup:")
            print("   Sur MacBook: python3 sync_logs.py --backup")
            return
        
        perf_log = latest / "performance_log.csv"
        trades_log = latest / "trades_log.csv"
        analyze_from_path(perf_log, trades_log)
    
    elif args.local:
        perf_log = Path("data") / "performance_log.csv"
        trades_log = Path("data") / "trades_log.csv"
        analyze_from_path(perf_log, trades_log)
    
    elif args.backup:
        backup_path = Path(args.backup)
        perf_log = backup_path / "performance_log.csv"
        trades_log = backup_path / "trades_log.csv"
        analyze_from_path(perf_log, trades_log)
    
    else:
        # Mode auto: essayer local, puis latest backup
        local_perf = Path("data") / "performance_log.csv"
        if local_perf.exists():
            print("📍 Mode: Analyse locale (data/)")
            analyze_from_path(local_perf, Path("data") / "trades_log.csv")
        else:
            latest = find_latest_backup()
            if latest:
                print("📍 Mode: Dernier backup (backups/)")
                perf_log = latest / "performance_log.csv"
                trades_log = latest / "trades_log.csv"
                analyze_from_path(perf_log, trades_log)
            else:
                print("❌ Aucun fichier trouvé")
                print("\n💡 Options:")
                print("   --local  : Analyser depuis data/")
                print("   --latest : Analyser depuis le dernier backup")


if __name__ == "__main__":
    main()
