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






   


if __name__ == "__main__":
    creer_base_si_absente(DB_FILE)

    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec_())

