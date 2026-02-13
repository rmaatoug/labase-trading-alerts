# labase-trading-alerts

Petit ensemble de scripts pour tester des signaux de breakout via Interactive Brokers
et envoyer des alertes via Telegram. Les scripts sont des exécutions simples (single-run)
et se trouvent à la racine; les helpers partagés sont dans `src/`.

Pré-requis
 - Python 3.10+ (ou 3.8+ compatible avec les dépendances listées)
 - Un environnement virtuel recommandé

Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configuration
 - Créer un fichier `.env` ou exporter ces variables d'environnement:
	 - `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID`
	 - `IBKR_HOST` (ex: 127.0.0.1)
	 - `IBKR_PORT` (ex: 7497)
	 - `IBKR_CLIENT_ID` (choisir un `clientId` non utilisé par d'autres scripts)

Vérifier la connectivité (Telegram + IBKR)
```bash
python src/main.py
```

Exemples d'exécution
 - Test de prix: `python price_check.py`
 - Calcul du signal de breakout: `python signal_breakout.py`
 - Script d'exécution en mode "paper" (renommé en .WIP pour éviter exécution accidentelle):
	 `python trade_breakout_multi_paper.WIP.py`
 - Exemple principal d'entrée en position (paper): `python trade_breakout_paper.py`

Conventions et points importants
 - Les scripts appellent `ib.connect()` / `ib.disconnect()` directement; ils sont synchrones.
 - Chaque script définit un `clientId` dans l'appel `ib.connect(...)`. Évitez les collisions
	 si vous lancez plusieurs scripts simultanément (ex: clientId 3,7,8,9 observés).
 - `trade_breakout_paper.py` et `trade_breakout_multi_paper.WIP.py` écrivent dans `trades_log.csv`
	 et appliquent une règle: une entrée par jour par symbole. Respectez cette logique si vous
	 modifiez le flux d'ordre.
 - Telegram envoie via `src/telegram_client.py` et lève des exceptions si le POST échoue.

Ajouts récents
 - `infra/metrics.py`: helper minimal pour compter/gauger métriques locales.
 - `scripts/start.sh`: wrapper qui active `caffeinate` uniquement sur macOS si présent,
	 puis lance `python3 src/main.py`.

## 🚀 Déploiement sur serveur cloud

Pour faire tourner le bot 24/7 sur un serveur Hetzner Cloud :

- **[QUICKSTART.md](QUICKSTART.md)** - Déploiement rapide en 15 minutes ⚡
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Guide complet étape par étape 📖
- **[SECURITY.md](SECURITY.md)** - Bonnes pratiques de sécurité 🔒

Scripts de déploiement disponibles :
- `scripts/setup_server.sh` - Installation automatique des dépendances
- `scripts/deploy_bot.sh` - Déploiement complet automatisé
- `scripts/start_ibgateway.sh` - Démarrage IB Gateway en mode headless
- `scripts/install_systemd_services.sh` - Services système pour redémarrage auto

Configuration IBC (IB Controller) :
- `config/ibc_config_template.ini` - Template de configuration IBC
- `config/trading-bot.service` - Service systemd pour le bot
- `config/ibgateway.service` - Service systemd pour IB Gateway

Besoin d'aide ?
 - Pour vérifier la configuration IBKR locale, assurez-vous que TWS/IB Gateway est lancé
	 et que l'API est activée (host/port corrects).
 - Si vous voulez que j'ajoute une action GitHub Actions pour valider `python src/main.py`,
	 dites-le et je peux générer un workflow minimal.
# -labase-trading-alerts