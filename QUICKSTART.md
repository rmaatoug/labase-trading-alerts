# Quickstart — Déploiement Alpaca Trading Bot

Guide rapide pour déployer le bot sur un serveur Ubuntu/Debian en **15 minutes**.

## Prérequis

1. **Serveur Ubuntu/Debian** (local, VPS, Hetzner, AWS, etc.)
2. **Compte Alpaca** (gratuit) : https://alpaca.markets
3. **Bot Telegram** : parler à @BotFather sur Telegram

## Étape 1 : Créer compte Alpaca (5 min)

1. Aller sur https://alpaca.markets
2. Créer un compte (gratuit, pas de CB requise pour paper trading)
3. Activer le 2FA (ne bloque pas l'API)
4. Aller dans **Account** → **Paper Trading** → **API Keys**
5. Générer une paire de clés :
   - `API Key ID` (commence par PK...)
   - `Secret Key` (à sauvegarder immédiatement)

## Étape 2 : Créer bot Telegram (2 min)

1. Ouvrir Telegram et parler à @BotFather
2. Envoyer `/newbot` et suivre les instructions
3. Récupérer le **token** (ex: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Chercher @userinfobot et récupérer votre **Chat ID** (ex: `987654321`)

## Étape 3 : Déployer sur serveur (8 min)

### SSH dans votre serveur

```bash
ssh user@votre-serveur-ip
```

### Déploiement automatique

```bash
# Clone du repo
cd ~
git clone https://github.com/rmaatoug/labase-trading-alerts.git
cd labase-trading-alerts

# Rendre les scripts exécutables
chmod +x scripts/*.sh

# Lancer le déploiement automatique
./scripts/deploy_bot.sh
```

Le script va :
- Installer Python 3 et dépendances
- Créer environnement virtuel
- Installer les packages Python
- Créer les dossiers nécessaires

### Configuration des clés API

```bash
# Copier le template
cp .env.example .env

# Éditer avec vos vraies clés
nano .env
```

Remplir :
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321

ALPACA_API_KEY=PKXXXXXXXXXXXXXXXXXXX
ALPACA_SECRET_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

Sauvegarder : `Ctrl+O`, `Enter`, `Ctrl+X`

### Test de connectivité

```bash
source venv/bin/activate
python3 src/main.py
```

Vous devriez voir :
```
Telegram: OK
Alpaca connected: True
Account equity: $100000.00
Buying power: $100000.00
```

Et recevoir un message Telegram !

### Lancer le bot

```bash
./scripts/start.sh
```

### Installer la surveillance automatique

```bash
./scripts/install_cron.sh
```

Cron jobs installés :
- **Watchdog (1h)** : Redémarre le bot s'il plante
- **Heartbeat (9h)** : Message quotidien de statut
- **Rapport (22h)** : Statistiques du jour
- **Rotation logs (0h)** : Nettoyage automatique

## Commandes utiles

```bash
# Vérifier le statut
./scripts/status.sh

# Voir les logs en temps réel
tail -f logs/bot.log

# Arrêter le bot
./scripts/stop.sh

# Redémarrer le bot
./scripts/stop.sh && ./scripts/start.sh

# Voir les trades
cat trades_log.csv

# Vérifier les cron jobs
crontab -l
```

## Architecture finale

```
Serveur Ubuntu/Debian
├── Python 3 + virtualenv
├── Bot Python (runner_5m.py)
│   ├── Analyse 29 tickers US toutes les 5 min
│   ├── Détecte breakouts
│   ├── Passe ordres via Alpaca API
│   └── Envoie alertes Telegram
├── Watchdog (cron 1h) → Redémarrage auto
├── Heartbeat (cron 9h) → Notification quotidienne
└── Rapport (cron 22h) → Statistiques du jour
```

## Troubleshooting

### Bot ne démarre pas

```bash
# Vérifier les logs
cat logs/runner.log
tail -20 logs/bot.log

# Tester manuellement
source venv/bin/activate
python3 src/main.py
```

### Erreur Alpaca authentication

Vérifier que dans `.env` :
- `ALPACA_API_KEY` commence par `PK` (paper) ou `AK` (live)
- `ALPACA_SECRET_KEY` est correct
- `ALPACA_BASE_URL=https://paper-api.alpaca.markets`

### Pas de notification Telegram

Vérifier que dans `.env` :
- `TELEGRAM_BOT_TOKEN` est correct
- `TELEGRAM_CHAT_ID` est votre ID (pas celui du bot)

Tester :
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Test"
```

### Le bot ne trade pas

- Vérifier horaires de marché US : 9h30-16h EST (lun-ven)
- Vérifier logs : `tail -f logs/bot.log`
- Vérifier tickers : `cat tickers.json` (uniquement US)

## Sécurité

- ✅ `.env` n'est jamais commité (dans .gitignore)
- ✅ Clés API stockées localement uniquement
- ✅ 2FA Alpaca ne bloque pas l'API
- ⚠️ Ne jamais partager vos clés API
- ⚠️ Utiliser paper trading avant live

## Support

- **Logs** : `logs/bot.log`, `logs/watchdog.log`, etc.
- **Trades** : `trades_log.csv`
- **GitHub** : https://github.com/rmaatoug/labase-trading-alerts

---

**C'est tout !** Votre bot tourne maintenant 24/7 sur Alpaca Paper Trading 🚀
