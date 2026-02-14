#!/bin/bash
# Script de déploiement complet du bot sur serveur Ubuntu/Debian
# Usage: ./scripts/deploy_bot.sh

set -e

echo "=== Déploiement bot Alpaca Trading ==="

# 1. Mise à jour système
echo "1. Mise à jour système..."
sudo apt update && sudo apt upgrade -y

# 2. Installation Python et dépendances
echo "2. Installation Python..."
sudo apt install -y python3 python3-pip python3-venv git

# 3. Clone ou pull du repo
if [ -d "$HOME/labase-trading-alerts" ]; then
    echo "3. Mise à jour du repo..."
    cd $HOME/labase-trading-alerts
    git pull
else
    echo "3. Clone du repo..."
    cd $HOME
    git clone https://github.com/rmaatoug/labase-trading-alerts.git
    cd labase-trading-alerts
fi

# 4. Création environnement virtuel
echo "4. Configuration environnement Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 5. Installation des packages Python
echo "5. Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Configuration .env
if [ ! -f ".env" ]; then
    echo "6. Configuration .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Éditer le fichier .env avec vos vraies clés:"
    echo "   nano .env"
    echo ""
    echo "   Remplir:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    echo "   - ALPACA_API_KEY"
    echo "   - ALPACA_SECRET_KEY"
    echo ""
else
    echo "6. .env existe déjà (pas écrasé)"
fi

# 7. Création dossier logs
echo "7. Création dossier logs..."
mkdir -p logs

# 8. Test connectivité
echo "8. Test de connectivité..."
echo "   Lancez: source venv/bin/activate && python3 src/main.py"
echo ""
echo "=== Déploiement terminé ==="
echo ""
echo "Prochaines étapes:"
echo "1. Éditer .env: nano .env"
echo "2. Tester: source venv/bin/activate && python3 src/main.py"
echo "3. Lancer bot: ./scripts/start.sh"
echo "4. Installer cron: ./scripts/install_cron.sh"
