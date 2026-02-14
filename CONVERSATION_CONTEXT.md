# Contexte de conversation — labase-trading-alerts

**Dernière mise à jour :** 14 février 2026 soir - Migration complète vers Alpaca ✅

> **⚠️ NOTE POUR L'IA** : À la fin de chaque session significative, demander à l'utilisateur si ce fichier doit être mis à jour avec les décisions/changements importants.
> **🚨 SÉCURITÉ** : Ne JAMAIS enregistrer d'identifiants, mots de passe ou tokens dans ce fichier.

---

## 🎯 MISSION GLOBALE
Bot de trading automatisé qui :
- Analyse **tickers US** toutes les 5 minutes (via `runner_5m.py`)
- Détecte breakout sur fenêtre 60-min (12 barres × 5 min)
- Passe des ordres Long avec stop automatique via **Alpaca API**
- Envoie **alertes Telegram INTELLIGENTES** (signal/trade/erreur seulement)
- Tourne **24/7 sur serveur** avec Alpaca Paper Trading (gratuit, $0 commission)

---

## 📋 STATUT ACTUEL

### 🚀 PRODUCTION - Alpaca Paper Trading

### Infrastructure
- ✅ **Serveur cloud** : Déployé et opérationnel 24/7
- ✅ **Alpaca API** : Paper Trading gratuit (https://alpaca.markets)
- ✅ **Telegram** : Bot configuré via `.env`
- ✅ **Surveillance** : Watchdog auto-restart + alertes Telegram
- ✅ **Cron jobs** : Watchdog (1h), Heartbeat (9h), Rotation logs (minuit)

### Logique Trading
- **Stratégie** : Breakout simple (close > HH des 60 dernières min)
- **Fenêtre** : N=12 barres (60 min avec barres 5min)
- **Risque** : 200€ par trade
- **Position** : Max 1 par ticker par jour (safeguard)
- **Stop** : Au plus bas des 60 min (breakout symétrique)

### Tickers Actifs
Stocks US liquides uniquement (Alpaca supporte US markets seulement).
Configuration dans `tickers.json`.

---

## 🔧 ARCHITECTURE

### Fichiers clés
- `runner_5m.py` → Boucle infinie, lance `trade_breakout_paper.py` toutes les 5 min
- `trade_breakout_paper.py` → Script principal de trading
- `tickers.json` → Configuration tickers (facile à modifier)
- `src/alpaca_client.py` → Helper Alpaca API (remplace ibkr_client.py)
- `src/telegram_client.py` → POST Telegram
- `infra/metrics.py` → Simple counter/gauge metrics
- `infra/notifier.py` → Formatage messages Telegram

### Flux d'exécution (tous les 5 min)
```
runner_5m.py (sleep jusqu'à prochain multiple de 5)
    ↓
    ├─ Écrit heartbeat (logs/last_heartbeat.txt)
    ├─ Déclenche daily_report.py à 22h si besoin
    ↓
python3 trade_breakout_paper.py
    ↓
    ├─ Connexion Alpaca API
    ├─ Pour chaque ticker:
    │   ├─ Récupère bars 5-min via Alpaca API
    │   ├─ Calcule HH/LL sur fenêtre N=12
    │   ├─ Test signal: close > HH?
    │   ├─ Si YES + qty > 0 + pas position: TRADE
    │   ├─ Notification Telegram si signal/trade/erreur
    │   ├─ Log dans trades_log.csv
    │   └─ Pause 0.5s
    ├─ Fin
    └─ Retour
```

---

## 📬 NOTIFICATIONS TELEGRAM

### Envoyées si :
- ✅ Signal détecté (`Signal=True`)
- ✅ Achat exécuté (`Action=ENTER_LONG`)
- ✅ Stop rempli (`stop_status=Filled`)
- ✅ Erreur critique API

### PAS envoyées si :
- ❌ `Signal=False` et `Action=NO_TRADE`
- ❌ Ticker bloqué (déjà tradé aujourd'hui)
- ❌ Pas assez de qty disponible

---

## ⚙️ VARIABLES D'ENVIRONNEMENT (requis)


Fichier `.env` (à créer localement et sur serveur) :
```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

ALPACA_API_KEY=your_alpaca_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

**⚠️ IMPORTANT** :
- Paper Trading URL : `https://paper-api.alpaca.markets` (**SANS** `/v2`)
- Live Trading URL : `https://api.alpaca.markets`
- Les clés Paper commencent par `PK` (Paper Key)
- Ne JAMAIS utiliser de clés Live avec l'URL Paper (erreur `unauthorized`)
- Le SDK Alpaca ajoute `/v2` automatiquement (ne jamais le mettre dans `.env`)

**Synthèse utile pour la prochaine session :**
- `.env` ne doit jamais être versionné ni écrasé par git pull (protégé par .gitignore)
- Pour Paper Trading, toujours : `ALPACA_BASE_URL=https://paper-api.alpaca.markets`
- Si tu modifies `.env`, toujours redémarrer le bot (`./scripts/stop.sh && ./scripts/start.sh`)
- Le bot tourne 24/7 sur le serveur Hetzner, analyse toutes les 5 min, et t’alerte sur Telegram en cas de problème ou de trade


**Setup initial** :
```bash
cp .env.example .env
nano .env  # Remplir les clés API
```

**⚠️ IMPORTANT** : `.env` n'est JAMAIS commité sur GitHub (protégé par .gitignore)

---

## 🚀 COMMANDES TEST

### Test connectivité Telegram + Alpaca
```bash
python3 src/main.py
```

### Run trading bot une fois
```bash
python3 trade_breakout_paper.py
```

### Check logs
```bash
tail -f logs/bot.log
cat trades_log.csv
```

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
- `api_errors` → Erreurs API

---

## 📊 REPORTING & ANALYSE

### Rapport quotidien (22h automatique)
- ✅ Envoi auto chaque jour à 22h via `runner_5m.py`
- ✅ Contenu : capital, activité du jour, positions ouvertes
- ✅ Métriques 30j : Sharpe ratio, max drawdown
- Script : `daily_report.py`

### Analyse de performance
```bash
python3 analyze_performance.py
python3 analyze_performance.py --days 30
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

## 🐛 TROUBLESHOOTING

### Error: Alpaca authentication failed
→ Vérifier `.env` : `ALPACA_API_KEY` et `ALPACA_SECRET_KEY` correctes

### Error: Alpaca market closed
→ Alpaca trading hours: 9h30-16h00 EST (lun-ven)

### Error: Insufficient buying power
→ Vérifier capital disponible dans Alpaca dashboard

### Bot ne démarre pas
→ Vérifier logs : `tail -f logs/bot.log`

---

## 📋 HISTORIQUE SESSION 14 FÉV 2026

**Migration complète vers Alpaca** :
- ✅ Supprimé tout le code IBKR
- ✅ Créé nouveau client Alpaca (`src/alpaca_client.py`)
- ✅ Migré tous les scripts de trading vers Alpaca
- ✅ Mis à jour requirements.txt (`alpaca-trade-api` au lieu d'`ib_insync`)
- ✅ Mis à jour .env et documentation
- ✅ Nettoyé CONVERSATION_CONTEXT.md (supprimé infos sensibles)
- ✅ Déployé sur GitHub
- ✅ Fix Python 3.12 incompatibilité → Python 3.11 via deadsnakes PPA
- ✅ Déployé sur serveur Hetzner (root@46.225.143.230)
- ✅ Bot opérationnel 24/7 avec cron jobs

**Notifications Telegram améliorées (commit 54e1f26)** :
- ✅ **runner_5m.py** : alertes crash fatal, erreur subprocess, arrêt manuel
- ✅ **trade_breakout_paper.py** : alertes pour toutes erreurs API
  - Erreur connexion Alpaca
  - Erreur récupération données (`get_historical_bars`)
  - Erreur récupération positions (`get_positions`)
  - Erreur placement ordre BUY
  - ⚠️ **Alerte critique** : échec stop-loss (position non protégée)
  - Erreur inattendue (catch-all)

**Raison migration** :
- IBKR : problèmes de déploiement serveur (dialogue bloquant non résolu après 6h)
- Alpaca : setup simple (15 min), API stable, paper trading gratuit, $0 commission

**Limitations acceptées** :
- Alpaca : US markets uniquement (pas EU/crypto)
- Tickers réduits de 38 → 29 (supprimé .PA, .AS, BTC-EUR)

**Infrastructure serveur** :
- Hetzner Cloud CX21 (Ubuntu 24.04)
- Python 3.11 dans venv
- Cron jobs : watchdog (1h), heartbeat (9h), rotation (minuit), report (22h)
- Bot lancé via nohup, PID dans logs/bot.pid

---

*Last tested: 14 fév 2026 22h → Bot en production 24/7 ✅  
Alertes Telegram actives pour toutes erreurs critiques 🚨*
