import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sqlite3
from src.config import DB_FILE
import pandas as pd

'''

import sqlite3

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(donnees)")
print(cursor.fetchall())


with sqlite3.connect(DB_FILE) as conn:
    cur = conn.cursor()
    rows = cur.execute("SELECT datetime FROM donnees LIMIT 5").fetchall()
    for r in rows:
        print(r[0])

with sqlite3.connect(DB_FILE) as conn:
    cur = conn.cursor()
    r = cur.execute("SELECT COUNT(*) FROM donnees WHERE chauffage1_pompe > 0").fetchone()
    print("Nb lignes chauffage actif :", r[0])

with sqlite3.connect(DB_FILE) as conn:
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT datetime, chauffage1_pompe
        FROM donnees
        WHERE chauffage1_pompe > 0
        LIMIT 5
    """).fetchall()

    for r in rows:
        print(r)




with sqlite3.connect(DB_FILE) as conn:
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM jours_actifs LIMIT 5").fetchall()
    print("Jours avec chauffage actif :", rows)
with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.execute("SELECT COUNT(*) FROM donnees WHERE chauffage1_pompe > 0 AND datetime IS NULL")
    print("⛔ Nb lignes chauffage actif SANS datetime :", cursor.fetchone()[0])
with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.execute("PRAGMA table_info(donnees)")
    for col in cursor.fetchall():
        print(col)

with sqlite3.connect(DB_FILE) as conn:
    for row in conn.execute("SELECT DISTINCT substr(datetime, 1, 10) FROM donnees WHERE chauffage1_pompe > 0 LIMIT 10"):
        print("📅 jour actif détecté :", row)


import pandas as pd
from synthese import calcul_synthese_periode
with sqlite3.connect(DB_FILE) as conn:
    # Supposons que tu as déjà un DataFrame `df` issu de ta base :
    df = pd.read_sql_query("SELECT * FROM donnees WHERE datetime BETWEEN '2024-12-01' AND '2024-12-02'", conn)

    # Transforme bien la colonne datetime si nécessaire
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")

    # Appel de la synthèse
    synthese = calcul_synthese_periode(df)

    # Affichage brut en console
    for cle, valeur in synthese.items():
        print(f"{cle} : {valeur}")
with sqlite3.connect(DB_FILE) as conn:
    def calcul_synthese_periode(df: pd.DataFrame) -> dict:
        synthese = {}

        if 'temperature_exterieur' in df:
            temp_ext = df['temperature_exterieur']
            synthese['temp_ext_moy'] = round(temp_ext.mean(), 1)
            synthese['temp_ext_min'] = round(temp_ext.min(), 1)
            synthese['temp_ext_max'] = round(temp_ext.max(), 1)

        if 'modulation_puissance_chaudiere' in df:
            active = df['modulation_puissance_chaudiere'] > 0
            durée = active.sum()  # en minutes
            synthese['durée_marche'] = f"{durée//60}h{durée%60}min"
            synthese['nombre_cycles'] = transitions

            if transitions > 0:
                moyenne_cycle = durée / transitions
                h, m = divmod(round(moyenne_cycle), 60)
                synthese['durée_moyenne_cycle'] = f"{h}h{m:02d}min"
            else:
                synthese['durée_moyenne_cycle'] = "—"



        if 'vis_bruleur_marche' in df:
            vis = df['vis_bruleur_marche'].fillna(0)
            transitions = (vis.shift(1) == 0) & (vis == 1)
            synthese['nb_cycles_combustion'] = int(transitions.sum())

        if 'ecs_pompe' in df:
            ecs_on = df['ecs_pompe'] == 1
            durée_ecs = ecs_on.sum()
            synthese['ecs_total_on'] = f"{durée_ecs//60}h{durée_ecs%60}min"

        if 'chauffage1_pompe' in df:
            chauf_on = df['chauffage1_pompe'] == 1
            durée_chauf = chauf_on.sum()
            synthese['chauffage_total_on'] = f"{durée_chauf//60}h{durée_chauf%60}min"

        return synthese


import sqlite3
import pandas as pd
from datetime import datetime

# --- Paramètres ---
db_path = DB_FILE
DATE = "2025-01-06"  # <-- à adapter selon tes besoins
TABLE_NAME = "donnees"  # ou la vue si tu en as une spécifique

# --- Connexion et récupération des données pour la date choisie ---
def charger_donnees(date_str):
    conn = sqlite3.connect(db_path)
    query = f"""
    SELECT datetime, modulation_puissance_chaudiere
    FROM {TABLE_NAME}
    WHERE DATE(datetime) = ?
    ORDER BY datetime
    """
    df = pd.read_sql_query(query, conn, params=(date_str,))
    conn.close()
    return df

# --- Analyse des cycles ---
def analyser_cycles(df):
    synthese = {}
    if 'modulation_puissance_chaudiere' not in df or df.empty:
        return {"message": "Pas de données disponibles"}

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")

    active = df['modulation_puissance_chaudiere'] > 0
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

# --- Lancement du test ---
if __name__ == "__main__":
    df = charger_donnees(DATE)
    resultats = analyser_cycles(df)

    print(f"Analyse pour le {DATE}")
    for k, v in resultats.items():
        print(f"{k:<25}: {v}")


from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
import pandas as pd
from src.synthese import charger_donnees, generer_synthese  # à adapter selon ton projet

class FenetreGraphique(QWidget):
    def __init__(self, date_str):
        super().__init__()
        self.setWindowTitle(f"Synthèse pour le {date_str}")
        self.resize(800, 600)

        # --- Layout principal ---
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- Chargement des données ---
        self.date_str = date_str
        self.df = charger_donnees(date_str)

        if self.df.empty:
            self.afficher_message("Aucune donnée disponible pour cette date.")
            return

        # --- Tracer graphique (à adapter selon ton code) ---
        self.afficher_graphique()

        # --- Génération de synthèse ---
        synthese = generer_synthese(self.df)
        texte = self.formater_synthese(synthese)

        self.label_synthese = QLabel(texte)
        self.label_synthese.setAlignment(Qt.AlignLeft)
        self.label_synthese.setStyleSheet("font-size: 14px; margin: 10px;")
        self.layout.addWidget(self.label_synthese)

    def afficher_graphique(self):
        # Placeholder : à remplacer par ton code existant de graphique
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        ax = figure.add_subplot(111)
        ax.plot(self.df["datetime"], self.df["modulation_puissance_chaudiere"], label="Modulation (%)")
        ax.set_title("Modulation puissance chaudière")
        ax.set_xlabel("Heure")
        ax.set_ylabel("%")
        ax.legend()
        figure.tight_layout()
        self.layout.addWidget(canvas)

    def formater_synthese(self, synthese: dict) -> str:
        lignes = []
        for cle, val in synthese.items():
            lignes.append(f"{cle} : {val}")
        return "\n".join(lignes)

    def afficher_message(self, texte):
        label = QLabel(texte)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 16px; color: red;")
        self.layout.addWidget(label)

        
EMOJIS = {
    "Température extérieure": "🌡️",
    "Durée de combustion": "🔥",
    "Nombre de cycles": "🔁",
    "Consommation estimée": "🪵"
}
for cle, val in synthese.items():
    prefix = next((emoji for mot, emoji in EMOJIS.items() if mot in cle), "")
    lignes.append(f"{prefix} {cle} : {val}")



from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication([])
label = QLabel("Hello PyQt5")
label.show()
app.exec_()



import pandas as pd
import matplotlib.pyplot as plt



# -------- 1. Fonction pour charger les données ECS --------
def charger_ecs_etat(start_date, end_date, db_path=DB_FILE):
    query = """
    SELECT datetime, ecs_etat
    FROM donnees
    WHERE date(datetime) BETWEEN ? AND ?
    ORDER BY datetime
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn, params=(start_date, end_date), parse_dates=["datetime"])
    conn.close()
    return df

# -------- 2. Fonction de décodage binaire --------
def ecs_etat_label(val):
    if val == 16912:
        return "preparation"
    elif val == 8208:
        return "confort"
    elif val == 8200:
        return "off"
    else:
        return "inconnu"

# -------- 3. Graphique ECS --------
def tracer_ecs_etendu(df):
    df["ecs_etat"] = df["ecs_etat"].apply(ecs_etat_label)
    plt.figure(figsize=(12, 3))
    ax = plt.gca()

    # Couleurs par état
    couleurs = {
        "preparation": "lightcoral",
        "confort": "orange",
    }

    # Recherche des zones consécutives par état
    etat_prec = None
    start = None

    for i in range(len(df)):
        etat = df["ecs_etat"].iloc[i]
        if etat != "off":
            if etat != etat_prec:
                if start is not None and etat_prec != "off":
                    ax.axvspan(start, df["datetime"].iloc[i], color=couleurs.get(etat_prec, "gray"), alpha=0.4)
                start = df["datetime"].iloc[i]
                etat_prec = etat
        else:
            if start is not None and etat_prec != "off":
                ax.axvspan(start, df["datetime"].iloc[i], color=couleurs.get(etat_prec, "gray"), alpha=0.4)
                start = None
                etat_prec = "off"

    # Dernier segment
    if start is not None and etat_prec != "off":
        ax.axvspan(start, df["datetime"].iloc[-1], color=couleurs.get(etat_prec, "gray"), alpha=0.4)

    ax.set_title("État ECS (zones colorées)")
    ax.set_xlabel("Date / Heure")
    ax.set_yticks([])
    ax.grid(True, axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()
# -------- 4. Exécution test --------
if __name__ == "__main__":
    debut = "2025-06-08"
    fin = "2025-06-09"

    df = charger_ecs_etat(debut, fin)
    if df.empty:
        print("Aucune donnée trouvée pour cette période.")
    else:
        tracer_ecs_etendu(df)
'

from src.graphique import tracer_ecs_etat_zones
from src.database import charger_donnees_periode  # si tu as déjà ça
from src.config import tracer_ecs_etat_label
start_date = "2025-06-10"
end_date = "2025-06-11"
df = charger_donnees_periode(start_date, end_date)

if not df.empty and "ecs_etat" in df.columns:
    tracer_ecs_etat_zones(df)
else:
    print("⚠️ Données indisponibles pour tracer l’ECS.")

    
        def valider_colonnes(self):
        colonnes_selectionnees = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        logger.info(f"Colonnes sélectionnées : {colonnes_selectionnees}")
        # (à toi de déclencher ici le graphique si besoin)
        if not colonnes_selectionnees:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez cocher au moins une colonne.")
            return

        if self.radio_unique.isChecked():
            date_debut = date_fin = self.calendrier.selectedDate().toString("yyyy-MM-dd")
        else:
            if not self.date_debut or not self.date_fin:
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une plage de dates.")
                return
            date_debut = self.date_debut.toString("yyyy-MM-dd")
            date_fin = self.date_fin.toString("yyyy-MM-dd")

            colonnes_avec_datetime = []

            # --- Gestion spécifique de 'ecs_etat' ---
            tracer_ecs_etat = "ecs_etat" in colonnes_selectionnees
            if tracer_ecs_etat:
                colonnes_selectionnees.remove("ecs_etat")  # On ne veut pas tracer la courbe brute

            # --- Gestion spécifique de 'chauffage1_statut' ---
            tracer_chauffage1 = "chauffage1_statut" in colonnes_selectionnees
            if tracer_chauffage1:
                colonnes_selectionnees.remove("chauffage1_statut")  # Ne pas tracer la courbe brute


            colonnes_avec_datetime = colonnes_selectionnees + ["datetime"]

            if tracer_ecs_etat:
                colonnes_avec_datetime.append("ecs_etat")

            if tracer_chauffage1:
                colonnes_avec_datetime.append("chauffage1_statut")

            # Supprime doublons éventuels
            colonnes_avec_datetime = list(dict.fromkeys(colonnes_avec_datetime))

            logger.info(f"Colonnes demandées en lecture : {colonnes_avec_datetime}")
            logger.debug(f"→ Colonnes SQL finales : {colonnes_avec_datetime}")


       
        df = lire_donnees_selectionnees(
            DB_FILE,
            colonnes_avec_datetime,
            date_debut,
            date_fin
            )
        if df.empty:
            QMessageBox.information(self, "Pas de données", "Aucune donnée trouvée pour cette période.")
            return 
        print(f"Colonnes actuelles dans le DataFrame : {df.columns.tolist()}")
        

        # --- Nettoyer page graphique avant d’ajouter ---
        for i in reversed(range(self.layout_graphique.count())):
            widget = self.layout_graphique.itemAt(i).widget()
            if widget and widget != self.canvas_graphique:
                widget.setParent(None)
        if not df.empty:
            # --- Ajouter le graphique ---
            self.canvas_graphique.tracer_donnees(df, zones=False)
            # --- Tracer état ECS en arrière-plan ---
            if tracer_ecs_etat:
                self.canvas_graphique.tracer_ecs_etat_zones(df[["datetime", "ecs_etat"]])

            # Tracer état chauffage1 en arrière-plan
            if tracer_chauffage1:
                self.canvas_graphique.tracer_chauffage_zones(df[["datetime", "chauffage1_statut"]])

            


        
        # --- Générer et afficher la synthèse ---
        
        self.date_debut = QDate.fromString(date_debut, "yyyy-MM-dd")
        self.date_fin = QDate.fromString(date_fin, "yyyy-MM-dd")

        self.generer_synthese_dates()
        self.label_synthese.setReadOnly(True)
        
        self.label_synthese.setStyleSheet("background-color: #f5f5f5; padding: 10px;")

        self.layout_graphique.addWidget(self.label_synthese)

        # ✅ Passer à la page graphique
        self.stacked_widget.setCurrentWidget(self.page_graphique)

        # --- Bouton retour ---
        bouton_retour = QPushButton("⬅️ Retour à la sélection")
        bouton_retour.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_selection))
        self.layout_graphique.addWidget(bouton_retour)

        # --- Afficher la page graphique ---
        self.stacked_widget.setCurrentWidget(self.page_graphique)

    def generer_synthese_dates(self):
        

        if not self.date_debut or not self.date_fin:
            self.label_synthese.setPlainText("⚠️ Aucune période sélectionnée.")
            return

        debut = self.date_debut.toString("yyyy-MM-dd")
        fin = self.date_fin.toString("yyyy-MM-dd")

        df = charger_donnees_periode(debut, fin, DB_FILE)

        if df.empty:
            self.label_synthese.setPlainText("⚠️ Aucune donnée disponible pour cette période.")
            return

        dico = generer_synthese(df)
        texte = "\n".join([f"{cle} : {val}" for cle, val in dico.items()])
        self.label_synthese.setPlainText(texte)


            def tracer_ecs_et_chauffage(self, df):
        self.figure.clear()
        ax1 = self.figure.add_subplot(211)
        ax2 = self.figure.add_subplot(212, sharex=ax1)

        if "ecs_etat" in df.columns:
            self.tracer_ecs_etat_zones(df[["datetime", "ecs_etat"]], ax=ax1)
        if "chauffage1_statut" in df.columns:
            self.tracer_chauffage_zones(df[["datetime", "chauffage1_statut"]], ax=ax2)

        ax2.set_xlabel("Date/Heure")
        ax1.set_title("État ECS")
        ax2.set_title("Statut Chauffage")

        self.figure.tight_layout()
        self.draw()
'''
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from config import DB_FILE

def charger_donnees_chauffage1(db_path, date_debut, date_fin):
    try:
        with sqlite3.connect(db_path) as conn:
            requete = """
                SELECT datetime, chauffage1_statut
                FROM donnees
                WHERE datetime BETWEEN ? AND ?
                ORDER BY datetime
            """
            df = pd.read_sql_query(requete, conn, params=(f"{date_debut} 00:00:00", f"{date_fin} 23:59:59"))
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["chauffage1_statut"] = df["chauffage1_statut"].astype("Int64")
        return df
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
        return pd.DataFrame()

def tracer_chauffage1_zones(df):
    if df.empty:
        print("❌ Aucune donnée à tracer.")
        return

    couleurs = {
        16: "blue",
        32: "red",
        1056: "pink",
        2097184: "green"
    }

    fig, ax = plt.subplots(figsize=(10, 4))

    current_value = None
    start_time = None

    for i in range(len(df)):
        valeur = df.iloc[i]["chauffage1_statut"]
        time = df.iloc[i]["datetime"]

        if current_value is None:
            current_value = valeur
            start_time = time
            continue

        if valeur != current_value or i == len(df) - 1:
            end_time = time
            if current_value in couleurs:
                ax.axvspan(start_time, end_time, color=couleurs[current_value], alpha=0.4)
            current_value = valeur
            start_time = time

    ax.plot(df["datetime"], df["chauffage1_statut"], drawstyle="steps-post", color="black", linewidth=0.8)
    ax.set_title("chauffage1_statut - Zones colorées")
    ax.set_xlabel("Date")
    ax.set_ylabel("Statut")
    ax.grid(True)

    # Légende personnalisée
    legend_elements = [
        Patch(facecolor=color, edgecolor='k', label=f"{code}")
        for code, color in couleurs.items()
    ]
    ax.legend(handles=legend_elements, title="Codes")

    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()  # ou self.draw() dans ton interface PyQt

if __name__ == "__main__":
    date_debut = "2025-01-01"
    date_fin = "2025-01-05"
    df = charger_donnees_chauffage1(DB_FILE, date_debut, date_fin)
    tracer_chauffage1_zones(df)

