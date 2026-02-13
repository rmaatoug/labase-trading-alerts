# Contexte de conversation — labase-trading-alerts

**Dernière mise à jour :** 13 février 2026 (Système de reporting et analyse automatisé)

> **⚠️ NOTE POUR L'IA** : À la fin de chaque session significative, demander à l'utilisateur si ce fichier doit être mis à jour avec les décisions/changements importants.

---

## 🎯 MISSION GLOBALE
Bot de trading automatisé qui :
- Analyse 29 tickers **toutes les 5 minutes** (via `runner_5m.py`)
- Détecte breakout sur fenêtre 60-min (12 barres × 5 min)
- Passe des ordres Long avec stop automatique
- Envoie **alertes Telegram INTELLIGENTES** (signal/trade/erreur seulement)
- Tourne **24/7 en local** sur MacBook avec TWS

---

## 📋 STATUT ACTUEL (LIVE)

### Infrastructure
- ✅ **MacBook local** : PC allumé 24/7 avec TWS/IBGateway actif
- ✅ **Cron job** : `runner_5m.py` lancé toutes les 5 min
- ✅ **IBKR** : Connecté via `127.0.0.1:7497` (API enabled)
- ✅ **Telegram** : Bot configuré et testé (tokens en `.bash_profile`)

### Logique Trading
- **Stratégie** : Breakout simple (close > HH des 60 dernières min)
- **Fenêtre** : N=12 barres (60 min)
- **Risque** : 200€ par trade
- **Position** : Max 1 par ticker par jour (safeguard)
- **Ordre qty** : Cappé à 500 (limite IBKR)
- **Stop** : Au plus bas des 60 min (breakout symétrique)

### Tickers Actifs (29)
```
AAPL AMGN AMSC AMZN ASML AZN BABA CVX DPRO ESLT GOOGL INFY LMT MANH 
META MRNA NFLX NVDA ORCL PFE PLTR QQQ RFL TGEN TME TSM VRT WIT XOM
```
*(Note: Enlevés 9 tickers indisponibles sur IBKR: AM.PA, BTC-EUR, DSY.PA, EL.PA, HO.PA, MC.PA, PARRO.PA, RMS.PA, SHELL.AS)*

---

## 🔧 ARCHITECTURE

### Fichiers clés
- `runner_5m.py` → Boucle infinie, lance `trade_breakout_paper.py` toutes les 5 min
- `trade_breakout_paper.py` → Charge tickers.json → boucle sur 29 symboles → 1 connexion IBKR
- `tickers.json` → Configuration tickers (facile à modifier)
- `src/ibkr_client.py` → Helper IBKR
- `src/telegram_client.py` → POST Telegram
- `infra/metrics.py` → Simple counter/gauge metrics
- `infra/notifier.py` → Formatage messages Telegram

### Flux d'exécution (tous les 5 min)
```
runner_5m.py (sleep jusqu'à prochain multiple de 5)
    ↓
python3 trade_breakout_paper.py
    ↓
    ├─ Connexion IBKR unique (clientId=7)
    ├─ Pour chaque ticker:
    │   ├─ Récupère 2 jours de bars 5-min
    │   ├─ Calcule HH/LL sur fenêtre N=12
    │   ├─ Test signal: close > HH?
    │   ├─ Si YES + qty > 0 + pas position: TRADE
    │   ├─ Notification Telegram si signal/trade/erreur
    │   ├─ Log dans trades_log.csv
    │   └─ Pause 0.5s
    ├─ Déconnexion IBKR
    └─ Fin
```

---

## 📬 NOTIFICATIONS TELEGRAM

### Envoyées si :
- ✅ Signal détecté (`Signal=True`)
- ✅ Achat exécuté (`Action=ENTER_LONG`)
- ✅ Stop rempli (`stop_status=Filled`)
- ✅ Erreur critique IBKR (codes 1100/1101/1102)

### PAS envoyées si :
- ❌ `Signal=False` et `Action=NO_TRADE`
- ❌ Ticker bloqué (déjà tradé aujourd'hui)
- ❌ Pas assez de qty disponible

### Résultat
Avant : ~38 notif/5 min (bruit)  
Après : ~0-3 notif/5 min (pertinent)

---

## 🐛 BUGS FIXÉS (Session 12 fév)

1. **ValueError in metrics.inc()** ✅
   - Problème : `inc(metrics, 'api_errors')` (mauvais paramètre)
   - Solution : Changé en `inc('api_errors')`

2. **Tickers invalides** ✅
   - Problème : 9 tickers non disponibles sur IBKR
   - Solution : Enlevés (38→29)

3. **Order qty trop élevée** ✅
   - Problème : RFL tentait qty=3623 → IBKR reject (limit 500)
   - Solution : Cappé qty à 500

---

## 🚀 COMMANDES TEST

### Sur MacBook local
```bash
# Test connectivité Telegram + IBKR
python3 src/main.py

# Run trading bot une fois
python3 trade_breakout_paper.py

# Check logs
tail -f logs/bot.log
cat trades_log.csv
```

### Important : `python3` requis (pas `python`)
MacBook a Python 3.9 alias en `python3`

---

## 📊 SURVEILLANCE

### Fichiers à observer
- `logs/bot.log` → Détail exécution, erreurs
- `trades_log.csv` → Historique trades (ts_utc, symbol, signal, action, qty, stop, status)
- `performance_log.csv` → Résumé quotidien (capital, win rate, P&L)

### Metrics collectées
- `orders_sent` → Nombre ordres lancés
- `orders_filled` → Ordres remplis
- `orders_rejected` → Rejets
- `api_errors` → Erreurs IBKR

---

## 🔍 ANALYSE DE PERFORMANCE

### Sur MacBook (local - méthode simple)
```bash
# Analyse complète
python3 analyze_performance.py

# Analyse période spécifique
python3 analyze_performance.py --days 30
python3 analyze_performance.py --days 7
```

### Sur Codespaces (après synchronisation)
```bash
# 1. Sur MacBook: créer backup et pusher
python3 sync_logs.py --backup
git add backups/ && git commit -m "backup logs" && git push

# 2. Sur Codespaces: récupérer et analyser
git pull
python3 analyze_synced.py --latest
```

### Workflow rapide analyse
```bash
# MacBook uniquement (recommandé)
python3 analyze_performance.py

# OU avec sync vers Codespaces
python3 sync_logs.py --backup && git push  # MacBook
git pull && python3 analyze_synced.py      # Codespaces
```

---

## 💡 POUR MODIFIER LA CONFIG

### Ajouter/retirer tickers
→ Éditer `tickers.json` uniquement (format JSON)

### Changer risque ou qty
→ Modifier `RISK_EUR` ou `MAX_POSITION_EUR` dans `trade_breakout_paper.py`

### Changer fenêtre breakout
→ Modifier `N=12` dans `trade_breakout_paper.py`

---

## ⚙️ VARIABLES D'ENVIRONNEMENT (requis)

**MIGRATION VERS .env** (13 fév 2026) :
- ✅ Configuration centralisée dans `.env` (local uniquement)
- ✅ Template `.env.example` commité sur GitHub
- ✅ Plus besoin de `~/.bash_profile` pour TOKEN/CHAT_ID
- ✅ Portabilité : facile à copier entre machines

Fichier `.env` (à créer localement) :
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
IBKR_HOST=127.0.0.1
IBKR_PORT=7497
IBKR_CLIENT_ID=7
```

**Setup initial** :
```bash
cp .env.example .env
nano .env  # Remplir TOKEN et CHAT_ID
```

---

## 📊 REPORTING & ANALYSE (Nouveau - 13 fév 2026)

### Notification de démarrage
- ✅ Message Telegram automatique au lancement du bot
- Format : "🚀 Bot démarré le YYYY-MM-DD HH:MM:SS"

### Rapport quotidien (22h automatique)
- ✅ Envoi auto chaque jour à 22h via `runner_5m.py`
- ✅ Contenu : capital, activité du jour, positions ouvertes
- ✅ Métriques 30j : Sharpe ratio, max drawdown
- ✅ Win rate et P&L si stops remplis
- Script : `daily_report.py` (appelé automatiquement)

### Historique de performance
- ✅ **`performance_log.csv`** : sauvegarde quotidienne automatique
- Colonnes : date, net_liquidation, available_funds, signals, entries, stops_filled, open_positions, win_rate_pct, pnl_usd
- **Jamais écrasé** : append only (ajout chaque jour)
- Protégé par `.gitignore` (reste local)

### Analyse et optimisation
- ✅ Script `analyze_performance.py` pour analyse détaillée
- Métriques calculées : Sharpe ratio, max drawdown, win rate moyen
- Recommandations automatiques selon les performances
- Usage : `python3 analyze_performance.py [--days 30]`

### Fonctions d'analyse (infra/summary.py)
- `calculate_win_rate()` : % de trades gagnants
- `calculate_pnl()` : Profit & Loss total
- `calculate_sharpe_ratio()` : Rendement ajusté du risque (annualisé)
- `calculate_max_drawdown()` : Perte max depuis le pic (%)
- `save_daily_performance()` : Sauvegarde auto dans performance_log.csv
- `load_performance_history()` : Charge historique pour analyse

### Fichiers locaux (pas sur GitHub)
- `trades_log.csv` → Tous les trades (détail par ticker)
- `performance_log.csv` → Résumé quotidien (pour analyse stratégique)
- `logs/bot.log` → Logs d'exécution

---

## 📌 NOTES POUR PROCHAINE SESSION

- ✅ Système stable et testé (12-13 fév 2026)
- ✅ Reporting quotidien automatisé (22h)
- ✅ Historique de performance sauvegardé
- ✅ Outils d'analyse prêts pour optimisation
- ✅ Configuration via .env (portabilité)
- ⚠️  **IMPORTANT** : Fichiers de performance en local uniquement (voir section ci-dessous)

**Prochaine fois** : Relire ce fichier au démarrage Codespace !

---

## 🔄 SYNCHRONISATION FICHIERS LOCAL ↔ CODESPACES

### Problématique
- Bot tourne en **local** (MacBook) → fichiers générés localement
- Analyse sur **Codespaces** → fichiers absents
- `.gitignore` bloque `trades_log.csv` et `performance_log.csv` (pour sécurité)

### Solutions envisagées (13 fév 2026)
1. **Upload manuel** : Copier fichiers vers Codespaces quand besoin d'analyse
2. **Script de backup** : Auto-upload vers GitHub (dossier backups/) ou cloud storage
3. **Analyse locale** : Utiliser `analyze_performance.py` directement sur MacBook

**Décision à prendre** : Choisir méthode de sync pour analyses futures

---

*Last tested: 13 fév 2026 → Notifications, reporting quotidien, analyse de performance ✅*
