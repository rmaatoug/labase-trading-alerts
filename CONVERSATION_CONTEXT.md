# Contexte de conversation — labase-trading-alerts

**Dernière mise à jour :** 12 février 2026

## État général
- ✅ Système de documentation de contexte mis en place
- ✅ Job `runner_5m.py` analyse déjà les tickers toutes les 5 min sur machine locale avec TWS actif
- ✅ Notifications Telegram configurées et fonctionnelles

## Tâches complétées (Session 12 février 2026)
1. ✅ Créé `tickers.json` avec 38 tickers (triés alphabétiquement)
2. ✅ Refactorisé `trade_breakout_paper.py` pour :
   - Charger les tickers depuis `tickers.json` (au lieu de code en dur)
   - Boucler sur tous les tickers en une seule exécution
   - Support multi-devise (EUR pour .PA, .AS, BTC-EUR; USD ailleurs)
   - Gestion d'erreurs robuste par ticker
   - Une seule connexion IBKR (pas de reconnexion à chaque ticker)

## Décisions importantes
- **Configuration tickers** : utiliser `tickers.json` pour facilité d'ajout/retrait
- **Convention** : à chaque nouvelle session Codespace, relire ce fichier
- **Sauvegarder décisions** : dire « synthétise dans CONVERSATION_CONTEXT.md »
- **Infrastructure locale** : PC allumé 24/7 avec TWS + cron pour `runner_5m.py`

## Notes pour les sessions suivantes
- Les 38 tickers sont gérés dynamiquement → modifier `tickers.json` sans toucher au code
- Chaque cycle de 5 min analyse tous les tickers et envoie notifications individuelles  
- Observer les logs dans `logs/bot.log` + `trades_log.csv` pour suivi des signaux/trades
