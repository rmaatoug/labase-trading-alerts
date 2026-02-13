#!/bin/bash
#
# Script d'arrêt IB Gateway et Xvfb
# Usage: ./stop_ibgateway.sh

echo "=========================================="
echo "🛑 Arrêt IB Gateway"
echo "=========================================="

# Arrêter IB Gateway
if pgrep -f "ibgateway" > /dev/null; then
    echo "🛑 Arrêt IB Gateway..."
    pkill -f ibgateway
    sleep 3
    
    # Forcer si nécessaire
    if pgrep -f "ibgateway" > /dev/null; then
        echo "⚠️  Forçage arrêt..."
        pkill -9 -f ibgateway
    fi
    echo "   ✅ IB Gateway arrêté"
else
    echo "   ℹ️  IB Gateway n'était pas actif"
fi

# Arrêter Xvfb
if pgrep -f "Xvfb" > /dev/null; then
    echo "🛑 Arrêt Xvfb..."
    pkill -f Xvfb
    sleep 1
    echo "   ✅ Xvfb arrêté"
else
    echo "   ℹ️  Xvfb n'était pas actif"
fi

echo ""
echo "✅ Arrêt terminé"
echo ""
