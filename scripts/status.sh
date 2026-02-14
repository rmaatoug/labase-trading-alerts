#!/bin/bash
# Vérifier le statut du bot
# Usage: ./scripts/status.sh

cd "$(dirname "$0")/.."

echo "=== Status Bot Trading Alpaca ==="
echo ""

# Check PID
if [ -f "logs/bot.pid" ]; then
    PID=$(cat logs/bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        UPTIME=$(ps -p $PID -o etime= | tr -d ' ')
        echo "✅ Bot actif (PID: $PID, uptime: $UPTIME)"
    else
        echo "❌ Bot arrêté (PID file obsolète)"
        rm logs/bot.pid
    fi
else
    echo "❌ Bot arrêté (pas de PID file)"
fi

echo ""

# Dernier heartbeat
if [ -f "logs/last_heartbeat.txt" ]; then
    HEARTBEAT=$(cat logs/last_heartbeat.txt)
    echo "💓 Dernier heartbeat: $HEARTBEAT"
else
    echo "⚠️  Pas de heartbeat trouvé"
fi

echo ""

# Dernières lignes du log
if [ -f "logs/bot.log" ]; then
    echo "📋 Dernières 5 lignes du log:"
    tail -5 logs/bot.log
else
    echo "⚠️  Pas de logs trouvés"
fi

echo ""

# Nombre de trades aujourd'hui
if [ -f "trades_log.csv" ]; then
    TODAY=$(date +%Y-%m-%d)
    TRADES_TODAY=$(grep "^$TODAY" trades_log.csv | wc -l)
    echo "📊 Trades aujourd'hui: $TRADES_TODAY"
else
    echo "⚠️  Pas de trades_log.csv"
fi
