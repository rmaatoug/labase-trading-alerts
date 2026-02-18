#!/usr/bin/env python3
"""
Rotation des logs - Évite que bot.log ne remplisse le disque
À lancer via cron tous les jours à 00h:
0 0 * * * cd ~/labase-trading-alerts && python3 log_rotation.py
"""

import gzip
import shutil
from datetime import datetime
from pathlib import Path

# Chargement automatique des variables d'environnement
from dotenv import load_dotenv
load_dotenv()

LOG_FILE = "logs/bot.log"
MAX_LOG_SIZE_MB = 50  # Rotation si > 50 MB
KEEP_ROTATED_LOGS = 10  # Garder 10 dernières archives


def get_file_size_mb(filepath):
    """Retourne la taille du fichier en MB"""
    try:
        return Path(filepath).stat().st_size / (1024 * 1024)
    except FileNotFoundError:
        return 0


def rotate_log():
    """Effectue la rotation du fichier de log"""
    log_path = Path(LOG_FILE)
    
    if not log_path.exists():
        print(f"✅ Pas de log à rotater ({LOG_FILE} n'existe pas)")
        return
    
    size_mb = get_file_size_mb(LOG_FILE)
    print(f"📊 Taille actuelle de {LOG_FILE}: {size_mb:.2f} MB")
    
    if size_mb < MAX_LOG_SIZE_MB:
        print(f"✅ Pas besoin de rotation (< {MAX_LOG_SIZE_MB} MB)")
        return
    
    # Créer archive avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"logs/bot_{timestamp}.log.gz"
    
    print(f"🔄 Rotation en cours: {LOG_FILE} → {archive_name}")
    
    # Compresser l'ancien log
    with open(LOG_FILE, 'rb') as f_in:
        with gzip.open(archive_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    # Créer nouveau log vide
    open(LOG_FILE, 'w').close()
    
    archive_size_mb = get_file_size_mb(archive_name)
    print(f"✅ Archive créée: {archive_name} ({archive_size_mb:.2f} MB)")
    
    # Nettoyer anciennes archives
    cleanup_old_archives()


def cleanup_old_archives():
    """Supprime les archives trop anciennes"""
    logs_dir = Path("logs")
    archives = sorted(logs_dir.glob("bot_*.log.gz"), reverse=True)
    
    if len(archives) <= KEEP_ROTATED_LOGS:
        print(f"✅ {len(archives)} archives conservées (max: {KEEP_ROTATED_LOGS})")
        return
    
    to_delete = archives[KEEP_ROTATED_LOGS:]
    print(f"🗑️  Suppression de {len(to_delete)} anciennes archives...")
    
    for archive in to_delete:
        archive.unlink()
        print(f"   Supprimé: {archive.name}")
    
    print(f"✅ Nettoyage terminé, {KEEP_ROTATED_LOGS} archives conservées")


def main():
    print(f"\n{'='*60}")
    print(f"🔄 LOG ROTATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    rotate_log()
    
    print(f"\n{'='*60}")
    print(f"✅ Rotation terminée")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
