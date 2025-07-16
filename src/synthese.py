#synthese

import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sqlite3
from src.config import DB_FILE
import pandas as pd
from datetime import datetime
db_path = DB_FILE

TABLE_NAME = "donnees"

'''
# --- Connexion et récupération des données pour la date choisie ---
def charger_donnees(date_str, db_path=DB_FILE):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT datetime, modulation_puissance_chaudiere, temperature_actuelle
    FROM {TABLE_NAME}
    WHERE DATE(datetime) = ?
    ORDER BY datetime
    """
    df = pd.read_sql_query(query, conn, params=(date_str,))
    conn.close()
    return df

'''


def charger_donnees_periode(start_date, end_date, db_path=DB_FILE):
    conn = sqlite3.connect(db_path)
    query = f"""
        SELECT datetime, modulation_puissance_chaudiere, temperature_actuelle
        FROM {TABLE_NAME}
        WHERE date(datetime) BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY datetime
    """
    df = pd.read_sql_query(query, conn, parse_dates=["datetime"])
    conn.close()
    return df


def estimer_conso_pellets(df, pci=4.4, rendement=0.80, puissance_nominale=14):
    if "modulation_puissance_chaudiere" not in df:
        return None

    modulation = df["modulation_puissance_chaudiere"].fillna(0).clip(lower=0)
    puissance_utile = (modulation / 100) * puissance_nominale
    puissance_fournie = puissance_utile / rendement
    energie_totale_kwh = (puissance_fournie * (1 / 60)).sum()
    conso_pellets_kg = energie_totale_kwh / pci
    return round(conso_pellets_kg, 2)

# --- Analyse des cycles ---
def analyser_cycles(df):

    synthese = {}

    
    if 'modulation_puissance_chaudiere' not in df or df.empty:
        return {"message": "Pas de données disponibles"}
    
    df = df.copy()

    if 'datetime' in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime")
    elif df.index.name != "datetime":
        df.index = pd.to_datetime(df.index)


    active = df['modulation_puissance_chaudiere'] .fillna(0) > 0
    durée = active.sum()  # en minutes (1 ligne = 1 minute)
    transitions = (active.astype(int).diff() == 1).sum()

    synthese["durée_marche"] = f"{durée//60}h{durée%60}min"
    synthese["nombre_cycles"] = transitions

    if transitions > 0:
        moyenne = durée / transitions
        h, m = divmod(round(moyenne), 60)
        synthese["durée_moyenne_cycle"] = f"{h}h{m:02d}min"
    else:
        synthese["durée_moyenne_cycle"] = "—"

    return synthese


def generer_synthese(df):
    synthese = {}

    if df.empty or "datetime" not in df.columns:
        return {"Erreur": "Données manquantes ou invalides."}

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")

    # Température extérieure
    if "temperature_actuelle" in df.columns:
        ext = df["temperature_actuelle"]
        synthese["Température extérieure (min)"] = round(ext.min(), 1)
        synthese["Température extérieure (max)"] = round(ext.max(), 1)
        synthese["Température extérieure (moy)"] = round(ext.mean(), 1)

    # Cycles et durée de combustion
    cycle_info = analyser_cycles(df)
    synthese.update(cycle_info)

    # Estimation conso pellets (toujours)
    conso = estimer_conso_pellets(df)
    synthese["Consommation estimée (kg)"] = conso

    return synthese

if __name__ == "__main__":
    start_date = "2025-06-10"
    end_date = "2025-06-14"

    df = charger_donnees_periode(start_date, end_date)

    if df.empty:
        print("Aucune donnée trouvée pour cette période.")
    else:
        synthese = generer_synthese(df)
        print(f"\n--- Synthèse du {start_date} au {end_date} ---")
        for cle, valeur in synthese.items():
            print(f"{cle} : {valeur}")
