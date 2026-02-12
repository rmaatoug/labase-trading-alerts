# Contexte de conversation — labase-trading-alerts

**Dernière mise à jour :** 12 février 2026

## État général
- ✅ Système de documentation de contexte mis en place
- ✅ Job `runner_5m.py` analyse 29 tickers toutes les 5 min sur machine locale avec TWS actif
- ✅ Notifications Telegram configurées (signal/trade/erreurs IBKR seulement)
- ✅ Tests locaux MacBook passés → système fonctionnel

## Tâches complétées (Session 12 février 2026)

### Phase 1 : Multi-ticker setup
1. ✅ Créé `tickers.json` avec configuration externalisée
2. ✅ Refactorisé `trade_breakout_paper.py` pour :
   - Charger les tickers depuis `tickers.json`
   - Boucle unique sur tous les tickers
   - Une seule connexion IBKR par cycle
   - Gestion d'erreurs robuste par ticker

### Phase 2 : Smart notifications
3. ✅ Notifications **SEULEMENT** si :
   - Signal détecté (breakout)
   - Trade exécuté (ENTER_LONG)
   - Stop/Vente rempli
   - Erreur critique (IBKR disconnect)

### Phase 3 : Bug fixes & cleanup
4. ✅ Fixé bug `inc()` dans metrics.py (appel incorrect)
5. ✅ Nettoyé tickers.json : **38 → 29 tickers** (enlevé indisponibles)
6. ✅ Ajouté cap qty à 500 (limite IBKR)

## Tickers actifs (29)
AAPL, AMGN, AMSC, AMZN, ASML, AZN, BABA, CVX, DPRO, ESLT, GOOGL, INFY, LMT, MANH, META, MRNA, NFLX, NVDA, ORCL, PFE, PLTR, QQQ, RFL, TGEN, TME, TSM, VRT, WIT, XOM

## Décisions importantes
- **Config externe** : `tickers.json` pour ajout/retrait sans code
- **Smart alerts** : réduire bruit notif (avant ~38/5min, après seulement signaux pertinents)
- **Ordre limit** : qty cappée à 500 (constraint IBKR)
- **Local 24/7** : PC allumé + cron `runner_5m.py`

## Notes pour sessions suivantes
- Pour relancer test : `python3 trade_breakout_paper.py` (note: python3 requis sur MacBook)
- Modifier tickers → éditer `tickers.json` uniquement
- Observer : `logs/bot.log` + `trades_log.csv` pour suivi
- Système stable et testé ✅
