# Contexte de conversation — labase-trading-alerts

**Dernière mise à jour :** 13 février 2026 - Session complète (Production ready ✅)

> **⚠️ NOTE POUR L'IA** : À la fin de chaque session significative, demander à l'utilisateur si ce fichier doit être mis à jour avec les décisions/changements importants.

---

## 🎯 MISSION GLOBALE
Bot de trading automatisé qui :
- Analyse **38 tickers** toutes les 5 minutes (via `runner_5m.py`)
- Détecte breakout sur fenêtre 60-min (12 barres × 5 min)
- Passe des ordres Long avec stop automatique
- Envoie **alertes Telegram INTELLIGENTES** (signal/trade/erreur seulement)
- Tourne **24/7 en local** sur MacBook avec IB Gateway

---

## 📋 STATUT ACTUEL (LIVE)

### 🚀 PRODUCTION - Lancé le 13 février 2026 à 18h45 (bot pid=2179)

### Infrastructure
- ✅ **MacBook local** : PC allumé 24/7 avec IB Gateway actif
- ✅ **IB Gateway** : Port 4002 (Paper Trading) - Plus stable que TWS
- ✅ **IBKR** : Connecté via `127.0.0.1:4002` (API enabled, Read-Only désactivé)
- ✅ **Cron jobs** : Watchdog (1h), Heartbeat (9h), Rotation logs (minuit) - INSTALLÉS
- ✅ **Telegram** : Bot configuré via `.env` (local)
- ✅ **Surveillance** : Watchdog auto-restart + alertes Telegram - ACTIF
- ✅ **Caffeinate** : macOS ne s'endormira pas pendant exécution bot

### Logique Trading
- **Stratégie** : Breakout simple (close > HH des 60 dernières min)
- **Fenêtre** : N=12 barres (60 min)
- **Risque** : 200€ par trade
- **Position** : Max 1 par ticker par jour (safeguard)
- **Ordre qty** : Cappé à 500 (limite IBKR)
- **Stop** : Au plus bas des 60 min (breakout symétrique)

### Tickers Actifs (38)
```
AAPL AM.PA AMGN AMSC AMZN ASML AZN BABA BTC-EUR CVX DPRO DSY.PA 
EL.PA ESLT GOOGL HO.PA INFY LMT MANH MC.PA META MRNA NFLX NVDA 
ORCL PARRO.PA PFE PLTR QQQ RFL RMS.PA SHELL.AS TGEN TME TSM VRT WIT XOM
```
*(Note: Tous les 38 tickers d'origine réintégrés le 13 fév 2026. Inclut actions EU (.PA, .AS) et crypto (BTC-EUR). Si erreurs IBKR, retirer les problématiques.)*

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
    ├─ Écrit heartbeat (logs/last_heartbeat.txt)
    ├─ Déclenche daily_report.py à 22h si besoin
    ↓
python3 trade_breakout_paper.py
    ↓
    ├─ Connexion IBKR unique (clientId=7)
    ├─ Pour chaque ticker (38 tickers):
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

## �️ SYSTÈME DE SURVEILLANCE (Nouveau - 13 fév 2026)

### Watchdog (toutes les heures)
- ✅ Script `watchdog.py` via cron
- Vérifie que `runner_5m.py` est actif
- **Redémarrage automatique** si bot arrêté
- Alerte Telegram si problème détecté
- Vérifie heartbeat (max 2h sans activité)

### Heartbeat matinal (9h quotidien)
- ✅ Script `heartbeat_morning.py` via cron
- Message quotidien "✅ BONJOUR - Status quotidien"
- Inclut : status bot, uptime, nb logs du jour
- **Assurance que tout fonctionne** chaque matin

### Rotation des logs (minuit quotidien)
- ✅ Script `log_rotation.py` via cron
- Rotation automatique si `bot.log` > 50 MB
- Compression gzip des anciennes archives
- Conservation des 10 dernières archives
- **Évite saturation disque**

### Installation cron jobs
```bash
# Sur MacBook, après git pull
cd ~/labase-trading-alerts
chmod +x scripts/install_cron.sh
./scripts/install_cron.sh
```

Cron jobs créés :
```
0 * * * * watchdog.py        # Toutes les heures
0 9 * * * heartbeat_morning.py  # 9h quotidien
0 0 * * * log_rotation.py    # Minuit quotidien
```

### Fichiers de surveillance
- `logs/last_heartbeat.txt` : timestamp du dernier cycle (écrit par runner_5m.py)
- `logs/watchdog.log` : logs du watchdog
- `logs/heartbeat.log` : logs heartbeat matinal
- `logs/rotation.log` : logs rotation

---

## �🐛 BUGS FIXÉS (Session 12 fév)

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

## � AMÉLIORATIONS SESSION 13 FÉV 2026

1. **Migration vers .env** ✅
   - Configuration centralisée dans `.env` (local)
   - Template `.env.example` commité sur GitHub
   - Plus simple à déployer

2. **IB Gateway configuré** ✅
   - Migration TWS → IB Gateway (plus stable 24/7)
   - Port 4002 (Paper Trading)
   - API Settings: Read-Only désactivé

3. **Système de surveillance complet** ✅
   - Watchdog (toutes les heures) : vérifie + redémarre bot
   - Heartbeat matinal (9h) : notification quotidienne
   - Rotation logs (minuit) : évite saturation disque

4. **Reporting et analyse** ✅
   - Rapport quotidien automatique (22h)
   - Sauvegarde performance_log.csv
   - Scripts d'analyse de performance
   - Synchronisation logs pour analyse sur Codespaces

5. **Fix urllib3/LibreSSL** ✅
   - Problème : Warning urllib3 v2 avec LibreSSL 2.8.3 (macOS system SSL)
   - Solution : Downgrade urllib3<2.0.0 dans requirements.txt
   - **Action requise** : `pip3 install -r requirements.txt` après git pull
   - Plus de warning au lancement

6. **38 tickers réintégrés** ✅
   - Tous les tickers d'origine (EU + crypto)
   - Test en live pour validation

---

## �🚀 COMMANDES TEST

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
IBKR_PORT=4002
IBKR_CLIENT_ID=7
```

**⚠️ IMPORTANT** : Port 4002 = IB Gateway Paper Trading (préféré 24/7)

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

- ✅ Système complet et prêt pour production (13 fév 2026)
- ✅ 38 tickers d'origine réintégrés (test en live)
- ✅ Reporting quotidien automatisé (22h)
- ✅ Système de surveillance actif (watchdog + heartbeat + rotation)
- ✅ Historique de performance sauvegardé
- ✅ Outils d'analyse prêts pour optimisation
- ✅ Configuration via .env (portabilité)
- ✅ Scripts de synchronisation pour analyse sur Codespaces
- ✅ **Guide de déploiement Hetzner Cloud créé** (13 fév 2026)
- ⚠️  **IMPORTANT** : Fichiers de performance en local uniquement (voir section ci-dessous)

---

## ☁️ DÉPLOIEMENT HETZNER CLOUD (Nouveau - 13 fév 2026)

### Documentation créée
- ✅ **QUICKSTART.md** : Déploiement rapide en 15 minutes
- ✅ **DEPLOYMENT.md** : Guide complet étape par étape
- ✅ **SECURITY.md** : Bonnes pratiques de sécurité

### Scripts de déploiement
- ✅ `scripts/setup_server.sh` : Installation automatique dépendances serveur
- ✅ `scripts/deploy_bot.sh` : Déploiement complet automatisé
- ✅ `scripts/start_ibgateway.sh` : Démarrage IB Gateway headless (Xvfb + IBC)
- ✅ `scripts/stop_ibgateway.sh` : Arrêt propre IB Gateway
- ✅ `scripts/install_systemd_services.sh` : Installation services système

### Configuration IBC/systemd
- ✅ `config/ibc_config_template.ini` : Template configuration IBC
- ✅ `config/ibgateway.service` : Service systemd IB Gateway
- ✅ `config/trading-bot.service` : Service systemd trading bot

### Workflow de migration MacBook → Hetzner
1. Créer serveur CX21 sur console.hetzner.com (~5€/mois)
2. Lancer `setup_server.sh` (install Python, Java, Xvfb, IBC)
3. Installer IB Gateway + configurer IBC avec identifiants IBKR
4. Lancer `deploy_bot.sh` (clone repo + install + start)
5. Installer services systemd pour redémarrage auto

### Avantages serveur cloud vs MacBook local
- ✅ Disponibilité 24/7 garantie (pas de mise en veille)
- ✅ Connexion internet stable
- ✅ Pas de dépendance matérielle personnelle
- ✅ Sauvegarde/snapshot facile
- ✅ Coût prévisible (~5€/mois)
- ✅ Redémarrage auto en cas de panne (systemd)

### Sécurité renforcée
- ✅ Firewall UFW configuré
- ✅ SSH par clé uniquement (pas de mot de passe)
- ✅ Fail2ban contre brute force
- ✅ Port API (4002) non exposé publiquement
- ✅ Fichiers sensibles protégés (chmod 600)
- ✅ Mises à jour automatiques système

### Prochaine étape si migration vers Hetzner
1. Lire QUICKSTART.md pour vue d'ensemble
2. Suivre DEPLOYMENT.md étape par étape
3. Vérifier SECURITY.md pour durcissement serveur
4. Tester en paper trading d'abord
5. Surveiller logs et Telegram quotidiennement

---

**Prochaine fois** : Relire ce fichier au démarrage Codespace !

**Checklist avant lancement 14 jours** :
1. `git pull` → Récupérer derniers changements
2. `pip3 install -r requirements.txt` → Fix urllib3 si nécessaire
3. MacBook : réglages énergie (jamais mettre en veille)
4. IB Gateway : lancer et vérifier connexion port 4002
5. Vérifier `.env` avec TOKEN et CHAT_ID corrects
6. Test connexion : `python3 src/main.py` (doit afficher OK)
7. Installer cron jobs : `./scripts/install_cron.sh` puis `crontab -l` pour vérifier
8. Lancer bot : `./scripts/start.sh`
9. Vérifier status : `./scripts/status.sh`
10. Observer premier cycle : `tail -f logs/bot.log`

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

**Décision prise** : Scripts de synchronisation créés (`sync_logs.py` et `analyze_synced.py`)

---

*Last tested: 13 fév 2026 → Système complet : notifications, reporting, surveillance, analyse ✅  
Prêt pour lancement 14 jours de trading automatisé 🚀*
