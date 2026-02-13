#!/bin/bash
# Installation automatique des cron jobs pour la surveillance du bot
# Usage: ./scripts/install_cron.sh

REPO_DIR="$HOME/labase-trading-alerts"

echo "📋 Installation des cron jobs pour labase-trading-alerts"
echo "=========================================================="
echo ""
echo "Répertoire: $REPO_DIR"
echo ""

# Créer fichier temporaire avec les cron jobs
TEMP_CRON=$(mktemp)

# Récupérer les cron jobs existants (sauf ceux de labase-trading-alerts)
crontab -l 2>/dev/null | grep -v "labase-trading-alerts" > "$TEMP_CRON"

# Ajouter les nouveaux cron jobs
cat >> "$TEMP_CRON" << EOF

# === labase-trading-alerts ===
# Watchdog: vérifier bot toutes les heures
0 * * * * cd $REPO_DIR && python3 watchdog.py >> logs/watchdog.log 2>&1

# Heartbeat matinal: notification quotidienne à 9h
0 9 * * * cd $REPO_DIR && python3 heartbeat_morning.py >> logs/heartbeat.log 2>&1

# Rotation logs: tous les jours à minuit
0 0 * * * cd $REPO_DIR && python3 log_rotation.py >> logs/rotation.log 2>&1

# Auto-start au démarrage système (optionnel - décommenter si souhaité)
# @reboot cd $REPO_DIR && sleep 30 && ./scripts/start.sh
EOF

# Installer le nouveau crontab
crontab "$TEMP_CRON"
rm "$TEMP_CRON"

echo "✅ Cron jobs installés avec succès !"
echo ""
echo "📋 Jobs configurés:"
echo "   • Watchdog (toutes les heures)"
echo "   • Heartbeat matinal (9h)"
echo "   • Rotation logs (minuit)"
echo ""
echo "🔍 Vérifier l'installation:"
echo "   crontab -l"
echo ""
echo "📊 Logs des scripts de surveillance:"
echo "   tail -f logs/watchdog.log"
echo "   tail -f logs/heartbeat.log"
echo "   tail -f logs/rotation.log"
echo ""
