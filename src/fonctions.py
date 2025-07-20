
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sqlite3
from src.config import DB_FILE
import logging

logger = logging.getLogger(__name__)


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
        logger.error("❌ Erreur lors de la lecture de la vue 'jours_actifs' :%s", e)
        logger.info(f"✅ {len(jours)} jours avec chauffage actifs")
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
        logger.error("❌ Erreur lors de la lecture des jours dans donnees :%s", e)
        logger.info(f"✅ {len(jours)} jours avec données")

        return []




