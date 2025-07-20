# main.py
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import os
from config import DB_FILE
from database import creer_base_si_absente, charger_csvs_par_batch
from interface import FenetrePrincipale
from PyQt5.QtWidgets import QApplication
import logging
logger = logging.getLogger(__name__)

   


if __name__ == "__main__":
    try:
        creer_base_si_absente(DB_FILE)
        logger.info("🚀 Lancement de l'application...")

        app = QApplication(sys.argv)
        fenetre = FenetrePrincipale()
        fenetre.show()
        logger.info("🖥️ Interface lancée.")
        sys.exit(app.exec_())

    except Exception as e:
        logger.error(f"❌ Erreur critique au démarrage de l'application : {e}")
        sys.exit(1)
