#!/bin/bash
# Déploiement automatisé du bot labase-trading-alerts sur un serveur Linux
# À exécuter depuis le dossier du repo cloné sur le serveur
set -e

# 1. Création et activation de l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installation des dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 3. Permissions sécurisées
chmod 600 .env
chmod 700 logs || mkdir logs && chmod 700 logs
chmod 700 .

# 4. Installation du service systemd
sudo cp labase-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable labase-bot
sudo systemctl restart labase-bot

# 5. Vérification du statut
sudo systemctl status labase-bot --no-pager

echo "\nDéploiement terminé. Vérifiez les logs avec : tail -f logs/bot.log"
