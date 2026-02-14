#!/bin/bash
# Script de fix Python 3.11 pour Alpaca Trading Bot
# Installe Python 3.11 et reconfigure l'environnement
# Usage: ./scripts/fix_python.sh

set -e

echo "=== Fix Python 3.11 pour Alpaca Trading Bot ==="
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erreur: Lancez ce script depuis le répertoire labase-trading-alerts"
    exit 1
fi

# 1. Ajouter le PPA deadsnakes (Python 3.11)
echo "📦 Ajout du PPA deadsnakes..."
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# 2. Installer Python 3.11 et dépendances
echo "🐍 Installation Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev build-essential

# 3. Supprimer ancien venv
if [ -d "venv" ]; then
    echo "🗑️  Suppression ancien venv..."
    rm -rf venv
fi

# 4. Créer nouveau venv avec Python 3.11
echo "🔧 Création nouveau venv avec Python 3.11..."
python3.11 -m venv venv

# 5. Activer venv
source venv/bin/activate

# 6. Vérifier version Python
echo ""
echo "✅ Version Python:"
python --version
echo ""

# 7. Mettre à jour pip
echo "⬆️  Mise à jour pip..."
pip install --upgrade pip wheel setuptools

# 8. Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# 9. Créer dossier logs
echo "📁 Création dossier logs..."
mkdir -p logs

echo ""
echo "=== Installation terminée ! ==="
echo ""

# 10. Test de connectivité (si .env existe)
if [ -f ".env" ]; then
    echo "🧪 Test de connectivité..."
    echo ""
    python src/main.py
    echo ""
    echo "✅ Si vous voyez 'Telegram: OK' et 'Alpaca connected: True', c'est bon !"
else
    echo "⚠️  Fichier .env non trouvé"
    echo ""
    echo "Prochaines étapes:"
    echo "1. Copier .env: cp .env.example .env"
    echo "2. Éditer .env: nano .env"
    echo "3. Remplir vos clés API (Telegram + Alpaca)"
    echo "4. Tester: source venv/bin/activate && python src/main.py"
fi

echo ""
echo "🚀 Pour lancer le bot: ./scripts/start.sh"
