#!/bin/bash
# Installation des cron jobs pour surveillance du bot
# Usage: ./scripts/install_cron.sh

set -e

REPO_PATH="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_PATH="$REPO_PATH/venv/bin/python3"

echo "=== Installation cron jobs ==="
echo "Repo: $REPO_PATH"
echo ""

# Vérifier que venv existe
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Environnement virtuel non trouvé. Lancez d'abord: ./scripts/deploy_bot.sh"
    exit 1
fi

# Créer fichier crontab temporaire
CRON_FILE="/tmp/trading_bot_cron_$$"

# Lire crontab existant (si existe)
crontab -l > "$CRON_FILE" 2>/dev/null || true

# Supprimer anciennes entrées de ce bot (si existent)
grep -v "labase-trading-alerts" "$CRON_FILE" > "${CRON_FILE}.tmp" || true
mv "${CRON_FILE}.tmp" "$CRON_FILE"

# Ajouter nouvelles entrées
cat >> "$CRON_FILE" << EOF

# labase-trading-alerts - Bot monitoring
# Watchdog: vérifie et redémarre le bot si nécessaire (toutes les heures)
0 * * * * cd $REPO_PATH && $PYTHON_PATH watchdog.py >> logs/watchdog.log 2>&1

# Heartbeat matinal: notification quotidienne (9h)
0 9 * * * cd $REPO_PATH && $PYTHON_PATH heartbeat_morning.py >> logs/heartbeat.log 2>&1

# Rotation des logs: nettoyage automatique (minuit)
0 0 * * * cd $REPO_PATH && $PYTHON_PATH log_rotation.py >> logs/rotation.log 2>&1

# Rapport quotidien: statistiques journalières (22h)
0 22 * * * cd $REPO_PATH && $PYTHON_PATH daily_report.py >> logs/daily_report.log 2>&1

EOF

# Installer le nouveau crontab
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "✅ Cron jobs installés:"
echo ""
echo "   - Watchdog (1h)         : Surveillance + redémarrage auto"
echo "   - Heartbeat (9h)        : Notification matinale"
echo "   - Rotation logs (0h)    : Nettoyage automatique"
echo "   - Rapport quotidien (22h): Statistiques du jour"
echo ""
echo "📋 Vérifier: crontab -l"
echo "📊 Logs cron:"
echo "   - logs/watchdog.log"
echo "   - logs/heartbeat.log"
echo "   - logs/rotation.log"
echo "   - logs/daily_report.log"
