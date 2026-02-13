#!/bin/bash
#
# Script de démarrage IB Gateway avec IBC
# Usage: ./start_ibgateway.sh
#
# Ce script démarre IB Gateway en mode headless (sans écran)
# via Xvfb et IBC pour automatisation du login

set -e

echo "=========================================="
echo "🚀 Démarrage IB Gateway"
echo "=========================================="

# Configuration
DISPLAY_NUM=1
IBC_DIR="$HOME/ibc"
GATEWAY_DIR="$HOME/Jts/ibgateway"

# Vérifier que IBC est installé
if [ ! -d "$IBC_DIR" ]; then
    echo "❌ IBC non trouvé dans $IBC_DIR"
    echo "   Lancez setup_server.sh d'abord"
    exit 1
fi

# Vérifier que config.ini existe et est configuré
if [ ! -f "$IBC_DIR/config.ini" ]; then
    echo "❌ Fichier de configuration IBC manquant"
    echo "   Copiez le template:"
    echo "   cp config/ibc_config_template.ini ~/ibc/config.ini"
    echo "   nano ~/ibc/config.ini  # Remplir username/password"
    exit 1
fi

# Vérifier que IB Gateway est installé
if [ ! -d "$GATEWAY_DIR" ]; then
    echo "❌ IB Gateway non installé"
    echo "   Suivez les instructions dans DEPLOYMENT.md"
    exit 1
fi

# Tuer les processus existants
echo "🔍 Vérification des processus existants..."
if pgrep -f "ibgateway" > /dev/null; then
    echo "⚠️  IB Gateway déjà en cours, arrêt..."
    pkill -f ibgateway || true
    sleep 2
fi

if pgrep -f "Xvfb" > /dev/null; then
    echo "⚠️  Xvfb déjà en cours, arrêt..."
    pkill -f "Xvfb :$DISPLAY_NUM" || true
    sleep 1
fi

# Démarrer Xvfb (serveur X virtuel)
echo "🖥️  Démarrage Xvfb..."
export DISPLAY=:${DISPLAY_NUM}
Xvfb :${DISPLAY_NUM} -screen 0 1024x768x24 &
XVFB_PID=$!
sleep 2

# Vérifier que Xvfb tourne
if ! ps -p $XVFB_PID > /dev/null; then
    echo "❌ Erreur démarrage Xvfb"
    exit 1
fi
echo "   ✅ Xvfb actif (PID: $XVFB_PID)"

# Démarrer IB Gateway avec IBC
echo "🤖 Démarrage IB Gateway via IBC..."
cd "$IBC_DIR"
./scripts/ibcstart.sh &
IBC_PID=$!

# Attendre que Gateway démarre (peut prendre 30-60 secondes)
echo "⏳ Attente démarrage Gateway (peut prendre 1 minute)..."
sleep 10

# Vérifier que le processus tourne
if pgrep -f "ibgateway" > /dev/null; then
    echo "   ✅ IB Gateway démarré"
else
    echo "   ⚠️  Gateway pas encore détecté, attente..."
    sleep 20
    if pgrep -f "ibgateway" > /dev/null; then
        echo "   ✅ IB Gateway démarré"
    else
        echo "   ❌ Erreur: Gateway ne démarre pas"
        echo "   Vérifiez les logs:"
        echo "   - IBC: ~/ibc/logs/ibc.log"
        echo "   - Gateway: ~/Jts/ibgateway/*/logs/"
        exit 1
    fi
fi

# Attendre que l'API soit prête
echo "⏳ Attente disponibilité API (port 4002)..."
for i in {1..30}; do
    if netstat -tuln 2>/dev/null | grep -q ":4002 "; then
        echo "   ✅ API prête (port 4002)"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ⚠️  API pas encore disponible après 30s"
        echo "   Le bot pourra réessayer automatiquement"
    fi
    sleep 1
done

echo ""
echo "=========================================="
echo "✅ IB Gateway démarré avec succès"
echo "=========================================="
echo ""
echo "📊 Processus actifs:"
ps aux | grep -E "(Xvfb|ibgateway)" | grep -v grep
echo ""
echo "📡 Port API:"
netstat -tuln 2>/dev/null | grep 4002 || echo "   (en attente...)"
echo ""
echo "📋 Commandes utiles:"
echo "   - Logs IBC     : tail -f ~/ibc/logs/ibc.log"
echo "   - Logs Gateway : tail -f ~/Jts/ibgateway/*/logs/ibgateway.log"
echo "   - Stopper      : ./stop_ibgateway.sh"
echo "   - Processus    : ps aux | grep ibgateway"
echo ""
echo "🎯 Vous pouvez maintenant lancer le bot:"
echo "   cd ~/labase-trading-alerts"
echo "   ./scripts/start.sh"
echo ""
