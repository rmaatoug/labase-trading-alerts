# Contexte de conversation — labase-trading-alerts

**Dernière mise à jour :** 12 février 2026 (Session complète terminée)

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

### Metrics collectées
- `orders_sent` → Nombre ordres lancés
- `orders_filled` → Ordres remplis
- `orders_rejected` → Rejets
- `api_errors` → Erreurs IBKR

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

Dans `~/.bash_profile` :
```bash
export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
export TELEGRAM_CHAT_ID="YOUR_CHAT_ID"
export IBKR_HOST="127.0.0.1"
export IBKR_PORT="7497"
export IBKR_CLIENT_ID="7"
```

---

## 📌 NOTES POUR PROCHAINE SESSION

- ✅ Système stable et testé (12 fév 2026)
- ✅ Aucun bug connu
- ✅ Job tournant en local sans intervention
- ✅ Historique complet dans CONVERSATION_CONTEXT.md
- Les 29 tickers nettoyés et validés
- Logs disponibles 24/7 pour debug

**Prochaine fois** : Relire ce fichier au démarrage Codespace !

---

*Last tested: 12 feb 2026, 15:10 EST → All 29 tickers analyzed clean, no errors ✅*
