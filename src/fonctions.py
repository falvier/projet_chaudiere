
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sqlite3
from src.config import DB_FILE, STYLE_COLONNE  # adapte si besoin
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure





    


def lire_jours_actifs(db_path=DB_FILE):
    """
    Lit la liste des jours avec chauffage actif depuis la vue SQL jours_actifs.
    Retourne une liste de chaînes de caractères au format 'YYYY-MM-DD'.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            curseur = conn.execute("SELECT jour FROM jours_actifs")
            jours = [row[0] for row in curseur.fetchall()]
            #print(f"Jours actifs: {jours}")
        return jours
    except Exception as e:
        print("❌ Erreur lors de la lecture de la vue 'jours_actifs' :", e)
        return []


def lire_jours_donnees(db_path=DB_FILE):
    """
    Lit la liste des jours distincts présents dans la table donnees.
    Retourne une liste de chaînes de caractères au format 'YYYY-MM-DD'.
    """
    try:
        with sqlite3.connect(db_path) as conn:
            curseur = conn.execute("""
                SELECT DISTINCT date AS jour
                FROM donnees
                ORDER BY jour
            """)
            jours = [row[0] for row in curseur.fetchall()]
        return jours
    except Exception as e:
        print("❌ Erreur lors de la lecture des jours dans donnees :", e)
        return []



#if __name__ == "__main__":
    # Test afficher_graphique pour un jour unique et colonnes d’exemple
    #tracer_donnees(['2025-01-07'], ['temperature_exterieur', 'chauffage1_pompe'])

    # Test afficher_graphique pour un intervalle de dates et colonnes d’exemple
    #afficher_graphique(['2025-01-07', '2025-01-09'], ['temperature_exterieur', 'chauffage1_depart_mesure'])

    # Test lire_jours_actifs : affiche la liste des jours avec chauffage actif
    #jours_actifs = lire_jours_actifs()
    #print("Jours avec chauffage actif :", jours_actifs)

    # Test lire_jours_donnees : affiche tous les jours distincts présents dans donnees
    #jours_donnees = lire_jours_donnees()
    #print("Jours avec données :", jours_donnees)
