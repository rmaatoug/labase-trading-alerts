#!/bin/bash
#
# Script d'installation automatique pour serveur Hetzner Cloud
# Usage: ./setup_server.sh
# Compatible: Ubuntu 22.04 LTS
#
# Ce script installe tout ce qui est nécessaire pour faire tourner
# le bot de trading 24/7 sur un serveur Linux distant.
#

set -e  # Arrêt en cas d'erreur

echo "=========================================="
echo "🚀 Installation environnement Trading Bot"
echo "=========================================="
echo ""

# Vérifier que le script est lancé en tant que sudo/root pour certaines commandes
if [ "$EUID" -eq 0 ]; then 
    SUDO=""
else 
    SUDO="sudo"
fi

echo "📦 Étape 1/8 : Mise à jour système..."
$SUDO apt update
$SUDO apt upgrade -y

echo ""
echo "🐍 Étape 2/8 : Installation Python 3.10+..."
$SUDO apt install -y python3 python3-pip python3-venv python-is-python3
python3 --version

echo ""
echo "📚 Étape 3/8 : Installation Git..."
$SUDO apt install -y git
git --version

echo ""
echo "🖥️  Étape 4/8 : Installation Xvfb (serveur X virtuel)..."
$SUDO apt install -y xvfb x11vnc xterm
echo "   -> Xvfb permettra à IB Gateway de tourner sans écran"

echo ""
echo "☕ Étape 5/8 : Installation Java 11 (requis pour IB Gateway)..."
$SUDO apt install -y openjdk-11-jre-headless
java -version

echo ""
echo "📡 Étape 6/8 : Installation outils réseau..."
$SUDO apt install -y net-tools curl wget unzip

echo ""
echo "🤖 Étape 7/8 : Téléchargement et installation IBC (IB Controller)..."
# IBC permet d'automatiser le login IB Gateway
cd ~
mkdir -p ~/ibc
cd ~/ibc

# Version stable IBC
IBC_VERSION="3.18.0"
wget "https://github.com/IbcAlpha/IBC/releases/download/${IBC_VERSION}/IBCLinux-${IBC_VERSION}.zip" -O ibc.zip
unzip -o ibc.zip
chmod +x *.sh */*.sh

echo "   -> IBC installé dans ~/ibc/"

echo ""
echo "⚙️  Étape 8/8 : Configuration environnement Python..."
# Installer les outils de build si besoin
$SUDO apt install -y build-essential python3-dev

echo ""
echo "=========================================="
echo "✅ Installation terminée avec succès !"
echo "=========================================="
echo ""
echo "📋 Résumé des installations :"
echo "   - Python : $(python3 --version)"
echo "   - Git    : $(git --version | head -n1)"
echo "   - Java   : $(java -version 2>&1 | head -n1)"
echo "   - Xvfb   : Installé"
echo "   - IBC    : Version ${IBC_VERSION}"
echo ""
echo "🎯 Prochaines étapes :"
echo "   1. Télécharger IB Gateway (voir DEPLOYMENT.md)"
echo "   2. Configurer IBC (~/ibc/config.ini)"
echo "   3. Cloner le repository labase-trading-alerts"
echo "   4. Créer virtualenv et installer requirements.txt"
echo "   5. Configurer .env avec TOKEN/CHAT_ID"
echo "   6. Lancer le bot !"
echo ""
echo "📖 Documentation complète : DEPLOYMENT.md"
echo ""
