@echo off
echo 🔧 Création de l’environnement virtuel...
python -m venv venv

echo 📦 Activation de l’environnement...
call venv\Scripts\activate.bat

echo 📥 Installation des dépendances...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Installation terminée.
echo Pour lancer l'application :
echo venv\Scripts\activate && python src\main.py
pause
