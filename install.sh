#!/bin/bash

echo "🔧 Création de l’environnement virtuel..."
python3 -m venv venv

echo "📦 Activation de l’environnement..."
source venv/bin/activate

echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Installation terminée. Lance l’application avec :"
echo "source venv/bin/activate && python src/main.py"
