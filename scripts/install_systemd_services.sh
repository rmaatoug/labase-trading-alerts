#!/bin/bash
#
# Script d'installation des services systemd
# Usage: sudo ./install_systemd_services.sh
#
# Installe le bot et IB Gateway comme services système
# pour redémarrage automatique au boot

set -e

# Vérifier root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Ce script doit être lancé avec sudo"
    exit 1
fi

echo "=========================================="
echo "⚙️  Installation services systemd"
echo "=========================================="
echo ""

# Répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Projet : $PROJECT_DIR"
echo ""

# Copier les fichiers service
echo "📋 Copie des fichiers service..."
cp "$PROJECT_DIR/config/ibgateway.service" /etc/systemd/system/
cp "$PROJECT_DIR/config/trading-bot.service" /etc/systemd/system/
echo "   ✅ Fichiers copiés"

# Recharger systemd
echo ""
echo "🔄 Rechargement systemd..."
systemctl daemon-reload
echo "   ✅ systemd rechargé"

# Activer les services (démarrage automatique au boot)
echo ""
echo "🚀 Activation des services..."
systemctl enable ibgateway.service
systemctl enable trading-bot.service
echo "   ✅ Services activés"

echo ""
echo "=========================================="
echo "✅ Installation terminée"
echo "=========================================="
echo ""
echo "📋 Commandes disponibles :"
echo ""
echo "IB Gateway:"
echo "   sudo systemctl start ibgateway    # Démarrer"
echo "   sudo systemctl stop ibgateway     # Arrêter"
echo "   sudo systemctl status ibgateway   # Status"
echo "   journalctl -u ibgateway -f        # Logs en direct"
echo ""
echo "Trading Bot:"
echo "   sudo systemctl start trading-bot  # Démarrer"
echo "   sudo systemctl stop trading-bot   # Arrêter"
echo "   sudo systemctl status trading-bot # Status"
echo "   journalctl -u trading-bot -f      # Logs en direct"
echo ""
echo "Les deux:"
echo "   sudo systemctl restart ibgateway trading-bot"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Les services démarreront automatiquement au boot"
echo "   2. Redémarrage auto en cas de crash"
echo "   3. Pour démarrer maintenant:"
echo "      sudo systemctl start ibgateway"
echo "      sleep 60  # Attendre que Gateway soit prêt"
echo "      sudo systemctl start trading-bot"
echo ""
