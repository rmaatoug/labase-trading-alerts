#!/bin/bash
#
# Script de déploiement automatique du bot de trading
# Usage: ./deploy_bot.sh
# 
# Prérequis : 
#   - setup_server.sh déjà exécuté
#   - IB Gateway installé et configuré
#   - Fichier .env prêt avec TOKEN/CHAT_ID
#

set -e

echo "=========================================="
echo "🚀 Déploiement Trading Bot"
echo "=========================================="
echo ""

# Configuration
BOT_DIR="$HOME/labase-trading-alerts"
REPO_URL="https://github.com/rmaatoug/labase-trading-alerts.git"

# Vérifier que les dépendances de base sont installées
echo "🔍 Vérification des prérequis..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 non installé. Lancez setup_server.sh d'abord."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git non installé. Lancez setup_server.sh d'abord."; exit 1; }
echo "   ✅ Prérequis OK"

# Cloner ou mettre à jour le repository
echo ""
echo "📥 Étape 1/7 : Récupération du code..."
if [ -d "$BOT_DIR" ]; then
    echo "   -> Repository déjà présent, mise à jour..."
    cd "$BOT_DIR"
    git pull origin main
else
    echo "   -> Clonage du repository..."
    git clone "$REPO_URL" "$BOT_DIR"
    cd "$BOT_DIR"
fi

# Créer l'environnement virtuel
echo ""
echo "🐍 Étape 2/7 : Configuration environnement Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   ✅ Virtualenv créé"
else
    echo "   ✅ Virtualenv déjà existant"
fi

# Activer virtualenv et installer dépendances
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "   ✅ Dépendances installées"

# Créer .env si pas existant
echo ""
echo "⚙️  Étape 3/7 : Configuration .env..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ⚠️  Fichier .env créé depuis .env.example"
        echo "   ⚠️  IMPORTANT : Éditez .env avec vos vraies valeurs !"
        echo ""
        echo "   Commands à lancer :"
        echo "   nano $BOT_DIR/.env"
        echo ""
        read -p "Appuyez sur Entrée une fois .env configuré..."
    else
        echo "   ❌ .env manquant et pas de .env.example"
        exit 1
    fi
else
    echo "   ✅ .env déjà configuré"
fi

# Créer les répertoires nécessaires
echo ""
echo "📁 Étape 4/7 : Création des répertoires..."
mkdir -p logs backups
echo "   ✅ Répertoires créés"

# Test de connexion
echo ""
echo "🔌 Étape 5/7 : Test des connexions..."
echo "   -> Test IBKR + Telegram..."
if python3 src/main.py; then
    echo "   ✅ Connexions OK"
else
    echo "   ❌ Erreur de connexion - vérifiez :"
    echo "      1. IB Gateway est lancé"
    echo "      2. .env contient les bonnes valeurs"
    echo "      3. Port 4002 est ouvert"
    exit 1
fi

# Installer les cron jobs
echo ""
echo "⏰ Étape 6/7 : Installation des cron jobs..."
chmod +x scripts/*.sh
if ./scripts/install_cron.sh; then
    echo "   ✅ Cron jobs installés"
    crontab -l
else
    echo "   ⚠️  Erreur installation cron - non bloquant"
fi

# Démarrer le bot
echo ""
echo "🚀 Étape 7/7 : Démarrage du bot..."
if ./scripts/start.sh; then
    echo "   ✅ Bot démarré"
else
    echo "   ❌ Erreur au démarrage"
    exit 1
fi

# Afficher le statut
sleep 3
echo ""
echo "📊 Vérification du statut..."
./scripts/status.sh

echo ""
echo "=========================================="
echo "✅ Déploiement terminé avec succès !"
echo "=========================================="
echo ""
echo "📋 Commandes utiles :"
echo "   - Status   : cd $BOT_DIR && ./scripts/status.sh"
echo "   - Logs     : tail -f $BOT_DIR/logs/bot.log"
echo "   - Stop     : cd $BOT_DIR && ./scripts/stop.sh"
echo "   - Restart  : cd $BOT_DIR && ./scripts/stop.sh && ./scripts/start.sh"
echo ""
echo "🔔 Vous devriez recevoir un message Telegram '🚀 Bot démarré'"
echo ""
echo "📖 Documentation : $BOT_DIR/DEPLOYMENT.md"
echo ""
