#!/bin/bash
# Démarrage du bot de trading
# Usage: ./scripts/start.sh

cd "$(dirname "$0")/.."

# Check si déjà lancé
if [ -f "logs/bot.pid" ]; then
    PID=$(cat logs/bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Bot déjà lancé (PID: $PID)"
        exit 1
    else
        echo "⚠️  PID file existe mais processus mort, nettoyage..."
        rm logs/bot.pid
    fi
fi

# Activer venv
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Lancez d'abord: ./scripts/deploy_bot.sh"
    exit 1
fi

source venv/bin/activate

# Vérifier .env
if [ ! -f ".env" ]; then
    echo "❌ Fichier .env non trouvé. Copiez .env.example et remplissez-le."
    exit 1
fi

# Lancer le bot en arrière-plan
echo "🚀 Démarrage du bot..."
nohup python3 runner_5m.py > logs/runner.log 2>&1 &
BOT_PID=$!

# Sauvegarder PID
echo $BOT_PID > logs/bot.pid
echo "✅ Bot lancé (PID: $BOT_PID)"
echo "📋 Logs: tail -f logs/bot.log"
echo "🛑 Arrêt: ./scripts/stop.sh"

# Envoyer notification démarrage
sleep 2
if ps -p $BOT_PID > /dev/null 2>&1; then
    echo "✅ Bot opérationnel"
else
    echo "❌ Erreur au démarrage, vérifier logs/runner.log"
    rm logs/bot.pid
    exit 1
fi
