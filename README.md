# labase-trading-alerts

Bot de trading automatisé qui détecte des signaux de breakout et passe des ordres via **Alpaca Markets**,
avec alertes Telegram. Les scripts sont simples (single-run) et se trouvent à la racine; 
les helpers partagés sont dans `src/`.

## Pré-requis
 - Python 3.10+ (ou 3.8+ compatible avec les dépendances listées)
 - Compte Alpaca (gratuit en paper trading : https://alpaca.markets)
 - Bot Telegram (pour les notifications)
 - Un environnement virtuel recommandé

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Créer un fichier `.env` à partir du template :
```bash
cp .env.example .env
nano .env  # Remplir avec vos vraies valeurs
```

Variables requises dans `.env` :
 - `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID`
 - `ALPACA_API_KEY` et `ALPACA_SECRET_KEY` (depuis votre compte Alpaca)
 - `ALPACA_BASE_URL` (https://paper-api.alpaca.markets/v2 pour paper trading)

## Vérifier la connectivité (Telegram + Alpaca)
```bash
python src/main.py
```

## Exemples d'exécution
 - Test de prix: `python price_check.py`
 - Calcul du signal de breakout: `python signal_breakout.py`
 - Script principal d'exécution: `python trade_breakout_paper.py`
 - Vérifier compte: `python account_check.py`

## Conventions et points importants
 - Les scripts utilisent l'API REST Alpaca (pas de connexion persistante).
 - `trade_breakout_paper.py` écrit dans `trades_log.csv` et applique une règle: 
   une entrée par jour par symbole.
 - Telegram envoie via `src/telegram_client.py` et lève des exceptions si le POST échoue.
 - **Alpaca supporte uniquement les actions US** (pas EU ou crypto).

## Ajouts récents
 - Migration complète d'Interactive Brokers vers Alpaca (14 fév 2026)
 - Client Alpaca (`src/alpaca_client.py`) avec API simple
 - Support paper trading gratuit illimité
 - Zéro commission sur les trades

## 🚀 Déploiement sur serveur cloud

Le bot peut tourner 24/7 sur un serveur cloud (Hetzner, AWS, etc.) :

- **[QUICKSTART.md](QUICKSTART.md)** - Déploiement rapide ⚡
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guide complet 📖
- **[SECURITY.md](SECURITY.md)** - Bonnes pratiques de sécurité 🔒

Scripts de déploiement disponibles :
- `scripts/setup_server.sh` - Installation automatique des dépendances
- `scripts/start.sh` - Démarrage du bot
- `scripts/stop.sh` - Arrêt propre du bot
- `scripts/status.sh` - Vérifier le statut
- `scripts/install_cron.sh` - Installer les cron jobs (watchdog, heartbeat, etc.)

## Besoin d'aide ?
 - Pour les API keys Alpaca : https://alpaca.markets (Account → Paper Trading → API Keys)
 - Pour créer un bot Telegram : parler à @BotFather sur Telegram
 - Vérifier les logs : `tail -f logs/bot.log`
 - Historique des trades : `cat trades_log.csv`
