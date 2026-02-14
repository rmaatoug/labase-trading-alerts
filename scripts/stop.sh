#!/bin/bash
# Arrêt du bot de trading
# Usage: ./scripts/stop.sh

cd "$(dirname "$0")/.."

if [ ! -f "logs/bot.pid" ]; then
    echo "❌ Pas de PID file. Bot non lancé ?"
    exit 1
fi

PID=$(cat logs/bot.pid)

if ps -p $PID > /dev/null 2>&1; then
    echo "🛑 Arrêt du bot (PID: $PID)..."
    kill $PID
    sleep 2
    
    # Force kill si toujours actif
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Force kill..."
        kill -9 $PID
    fi
    
    rm logs/bot.pid
    echo "✅ Bot arrêté"
else
    echo "⚠️  Processus $PID n'existe pas, nettoyage PID file"
    rm logs/bot.pid
fi
