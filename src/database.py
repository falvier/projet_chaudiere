#database.py
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))


import pandas as pd
import sqlite3
from src.config import DATA_DIR, DB_FILE, RENAME_DICT
from tqdm import tqdm
import logging
logger = logging.getLogger(__name__)


def charger_csvs_par_batch(batch_size=50, update_progress_callback=None):
    fichiers_csv = list(DATA_DIR.glob("*.csv"))
    total = len(fichiers_csv)
    if total == 0:
        raise FileNotFoundError("Aucun fichier CSV trouvé dans le dossier data.")

    dataframes = []
    for i in range(0, total, batch_size):
        batch = fichiers_csv[i:i + batch_size]
        for j, fichier in enumerate(batch, start=i + 1):
            try:
                df = pd.read_csv(
                    fichier,
                    sep=';',
                    decimal=',',
                    dayfirst=True,
                    encoding='ISO-8859-1',
                    skipinitialspace=True
                )
                df.columns = df.columns.str.strip()
                df.rename(columns=RENAME_DICT, inplace=True)
                df.dropna(axis=1, how='all', inplace=True)

                if 'date' in df.columns and 'heure' in df.columns:
                    df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
                    df['heure'] = pd.to_datetime(df['heure'], format='%H:%M:%S').dt.strftime('%H:%M:%S')
                    df["datetime"] = pd.to_datetime(df["date"] + ' ' + df["heure"])
                    df["datetime"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
                    dataframes.append(df)
            except Exception as e:
                logger.error(f"❌ Erreur {fichier.name} : {e}")

            if update_progress_callback:
                update_progress_callback(j)

    if not dataframes:
        raise ValueError("Aucun fichier CSV valide.")
    
    return pd.concat(dataframes, ignore_index=True)

# Types par défaut à affecter selon le nom ou la logique simple
def infer_sql_type(colname):
    if "date" in colname or "heure" in colname:
        return "TEXT"
    elif "etat" in colname or "status" in colname or "moteur" in colname or "capteur" in colname:
        return "INTEGER"
    else:
        return "REAL"  # valeur flottante par défaut

def creer_table_dynamique(conn):
    colonnes_sql = []
    # Colonnes datetime, date et heure en tant que TEXT, NOT NULL
    colonnes_sql.append("datetime TEXT")
    colonnes_sql.append("date TEXT NOT NULL")
    colonnes_sql.append("heure TEXT NOT NULL")


    # Ajout des autres colonnes (sans date/heure/timestamp/datetime)
    for nouveau_nom in RENAME_DICT.values():
        if nouveau_nom not in ("timestamp", "date", "heure", "datetime"):  # on exclut ceux qu'on gère à part
            col_type = infer_sql_type(nouveau_nom)
            colonnes_sql.append(f"{nouveau_nom} {col_type}")

    # Clé primaire composite
    colonnes_sql.append("PRIMARY KEY (date, heure)")

    colonnes_str = ",\n  ".join(colonnes_sql)
    create_sql = f"CREATE TABLE IF NOT EXISTS donnees (\n  {colonnes_str}\n);"

    with conn:
        conn.execute(create_sql)

def inserer_donnees(conn, df):
    if df.empty:
        logger.info("⚠️ DataFrame vide, aucune donnée à insérer.")
        return

    colonnes = list(df.columns)

    # Vérifie que les noms de colonnes sont valides (alphanumériques + underscores uniquement)
    colonnes_valides = [col for col in colonnes if col and col.isidentifier()]
    if not colonnes_valides:
        logger.info("⚠️ Aucune colonne valide pour l'insertion SQL.")
        #print("Colonnes détectées :", colonnes)
        return

    placeholders = ', '.join(['?'] * len(colonnes_valides))
    colonnes_sql = ', '.join(colonnes_valides)

    requete_sql = f"INSERT OR IGNORE INTO donnees ({colonnes_sql}) VALUES ({placeholders})"
    donnees = [tuple(row[col] for col in colonnes_valides) for _, row in df.iterrows()]
    
    with conn:
        conn.executemany(requete_sql, donnees)

def jours_avec_donnees(db_path=DB_FILE):
    """Retourne la liste des jours pour lesquels il existe au moins une ligne de données."""
    requete = """
        SELECT DISTINCT date
        FROM donnees
        ORDER BY date;
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(requete)
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"❌ Erreur lors de la lecture des jours avec données : {e}")
        return []

def creer_vue_jours_actifs(db_path=DB_FILE):
    #print("📁 Lecture de la vue dans :", db_path)
    requete = """
    CREATE VIEW IF NOT EXISTS jours_actifs AS
    SELECT 
        substr(datetime, 1, 10) AS jour,
        COUNT(*) AS duree_minutes,
        MIN(datetime) AS debut,
        MAX(datetime) AS fin,
        ROUND((JULIANDAY(MAX(datetime)) - JULIANDAY(MIN(datetime))) * 24 * 60) AS duree_minutes
    FROM donnees
    WHERE chauffage1_pompe > 0
    GROUP BY substr(datetime, 1, 10)
    HAVING duree_minutes >= 5
    ORDER BY substr(datetime, 1, 10);
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute(requete)
            logger.info("✅ Vue 'jours_actifs' créée ou mise à jour avec succès.")
    except Exception as e:
        logger.error("❌ Erreur lors de la création de la vue :%s", e)

def lire_donnees_selectionnees(db_path, colonnes, date_debut, date_fin):
    """
    Lit les données de la table `donnees` entre deux dates, avec les colonnes demandées.
    """
    try:
        champs = ", ".join(dict.fromkeys(['datetime'] + colonnes))
        requete = f"""
            SELECT {champs}
            FROM donnees
            WHERE datetime BETWEEN ? AND ?
            ORDER BY datetime
        """
        logger.debug(f"→ SQL généré : SELECT {colonnes} ...")

        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(requete, conn, params=(f"{date_debut} 00:00:00", f"{date_fin} 23:59:59"))
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    except Exception as e:
        logger.error("❌ Erreur lors de la lecture des données :%s", e)
        return pd.DataFrame()

def creer_base_si_absente(db_path=DB_FILE):
    if not Path(db_path).exists():
        logger.info("⚙️ Base de données absente, création en cours...")

        try:
            df = charger_csvs_par_batch()
            logger.info("📊 Données chargées, création de la table...")
            conn = sqlite3.connect(db_path)
            creer_table_dynamique(conn)
            inserer_donnees(conn, df)
            creer_vue_jours_actifs(db_path)
            conn.close()
            logger.info("✅ Base de données créée avec succès.")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de la base : {e}")
    else:
        logger.info("✅ Base de données déjà présente.")



def initialiser_base(_=None):
    conn = sqlite3.connect(DB_FILE)
    df = charger_csvs_par_batch()
    creer_table_dynamique(conn)
    inserer_donnees(conn, df)
    creer_vue_jours_actifs()
    conn.close()

def charger_donnees_sqlite_par_colonnes(nom_table, colonnes):
    """
    Charge depuis une table SQLite les colonnes spécifiées, avec sécurité.
    Renvoie un DataFrame vide si une erreur survient.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        colonnes_str = ", ".join(colonnes)
        query = f"SELECT {colonnes_str} FROM {nom_table}"
        df = pd.read_sql_query(query, conn)
        conn.close()

        logger.info(f"🔎 Colonnes demandées : {colonnes}")
        logger.info(f"✅ Colonnes lues : {df.columns.tolist()}")
        return df

    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des colonnes depuis {nom_table} : {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    initialiser_base()
    logger.info("Base de données initialisée avec la vue datetime.")
 
