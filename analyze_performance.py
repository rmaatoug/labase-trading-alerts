#!/usr/bin/env python3
"""
Script d'analyse de performance - pour optimiser la stratégie
Usage: python3 analyze_performance.py [--days 30]
"""

import argparse
from infra.summary import (
    load_performance_history,
    calculate_sharpe_ratio,
    calculate_max_drawdown
)


def print_performance_report(days: int = None):
    """Affiche un rapport de performance détaillé"""
    
    history = load_performance_history(days=days)
    
    if not history:
        print("❌ Aucune donnée de performance disponible")
        print("   Le fichier performance_log.csv sera créé après le premier rapport quotidien")
        return
    
    period = f"sur {len(history)} jours" if days is None else f"sur les {min(len(history), days)} derniers jours"
    print(f"\n📊 ANALYSE DE PERFORMANCE {period}\n")
    print("=" * 60)
    
    # Capital
    first = history[0]
    last = history[-1]
    start_capital = float(first.get('net_liquidation', 0))
    end_capital = float(last.get('net_liquidation', 0))
    pnl_total = end_capital - start_capital
    pnl_pct = (pnl_total / start_capital * 100) if start_capital > 0 else 0
    
    print(f"\n💰 CAPITAL")
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
    
    # Recommandations
    print(f"\n🎯 RECOMMANDATIONS")
    
    if len(history) < 30:
        print(f"  • Attendre au moins 30 jours pour optimiser la stratégie")
    else:
        if win_rates and avg_win_rate < 50:
            print(f"  • Win rate faible: considérer d'élargir les stops")
        
        if total_signals > 0 and signal_to_trade < 30:
            print(f"  • Peu de signaux exécutés: vérifier les contraintes de risque")
        
        if len(history) >= 2 and sharpe < 0:
            print(f"  • Sharpe négatif: revoir la stratégie (fenêtre, stops, etc.)")
    
    print("\n" + "=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Analyse de performance du bot de trading")
    parser.add_argument('--days', type=int, default=None, 
                       help='Nombre de jours à analyser (par défaut: tous)')
    
    args = parser.parse_args()
    print_performance_report(days=args.days)


if __name__ == "__main__":
    main()
