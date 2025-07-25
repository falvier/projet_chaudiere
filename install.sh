#!/bin/bash

echo "🔍 Vérification de l’environnement..."

# Vérifie si python3-venv est installé
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "⚠️ python3-venv n’est pas installé. Installation en cours..."
    sudo apt update && sudo apt install -y python3-venv
fi

# Vérifie si pip est installé
if ! command -v pip >/dev/null 2>&1; then
    echo "⚠️ pip n’est pas installé. Installation en cours..."
    sudo apt install -y python3-pip
fi

echo "🔧 Création de l’environnement virtuel..."
python3 -m venv venv

echo "📦 Activation de l’environnement..."
source venv/bin/activate

echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installation terminée. Lance l’application avec :"
echo "source venv/bin/activate && python src/main.py"
