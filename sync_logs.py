#!/usr/bin/env python3
"""
Script de synchronisation des logs pour analyse sur Codespaces
Usage: python3 sync_logs.py [--backup]

Options:
  --backup : Créer un backup horodaté dans backups/ (sera commitable sur GitHub)
  (défaut) : Copier vers data/ pour analyse locale uniquement
"""

import argparse
import shutil
import os
from datetime import datetime
from pathlib import Path


SOURCE_FILES = [
    "trades_log.csv",
    "performance_log.csv",
    "logs/bot.log"
]

BACKUP_DIR = "backups"  # Commitable sur GitHub
DATA_DIR = "data"        # Local uniquement (.gitignore)


def sync_to_backup():
    """Copie les logs vers backups/ avec timestamp (pour commit Git)"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(BACKUP_DIR) / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for source in SOURCE_FILES:
        source_path = Path(source)
        if source_path.exists():
            dest = backup_path / source_path.name
            shutil.copy2(source_path, dest)
            print(f"✅ Copié: {source} → {dest}")
            copied += 1
        else:
            print(f"⚠️  Ignoré (introuvable): {source}")
    
    if copied > 0:
        print(f"\n📦 Backup créé: {backup_path}")
        print(f"🔧 Pour commiter sur GitHub:")
        print(f"   git add {BACKUP_DIR}/{timestamp}")
        print(f'   git commit -m "backup: logs du {datetime.now().strftime("%Y-%m-%d")}"')
        print(f"   git push")
    else:
        print("\n❌ Aucun fichier copié")


def sync_to_data():
    """Copie les logs vers data/ pour analyse locale (pas commité)"""
    
    data_path = Path(DATA_DIR)
    data_path.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    for source in SOURCE_FILES:
        source_path = Path(source)
        if source_path.exists():
            dest = data_path / source_path.name
            shutil.copy2(source_path, dest)
            print(f"✅ Copié: {source} → {dest}")
            copied += 1
        else:
            print(f"⚠️  Ignoré (introuvable): {source}")
    
    if copied > 0:
        print(f"\n📊 Fichiers prêts pour analyse locale dans {DATA_DIR}/")
        print(f"💡 Ces fichiers ne seront pas commités (protégés par .gitignore)")
    else:
        print("\n❌ Aucun fichier copié")


def main():
    parser = argparse.ArgumentParser(
        description="Synchronise les logs pour analyse"
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Créer un backup horodaté dans backups/ (commitable sur GitHub)'
    )
    
    args = parser.parse_args()
    
    print("🔄 Synchronisation des logs...\n")
    
    if args.backup:
        sync_to_backup()
    else:
        sync_to_data()


if __name__ == "__main__":
    main()
