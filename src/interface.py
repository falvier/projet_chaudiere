import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
# interface_calendrier.py

from PyQt5.QtWidgets import (QApplication,
                             QWidget,
                             QVBoxLayout,
                             QCalendarWidget,
                             QLabel,
                             QMessageBox,
                             QRadioButton,
                             QButtonGroup,
                             QHBoxLayout,
                             QPushButton,
                             QStackedWidget,
                             QCheckBox,
                             QScrollArea,
                             QGridLayout,
                             QProgressBar,
                             QTextEdit
                             )
from PyQt5.QtGui import (QTextCharFormat,
                         QColor
                        )
from PyQt5.QtCore import (QDate,
                          Qt,
                          QObject,
                          pyqtSignal
                          )
                        
                        

from src.config import DB_FILE, COLONNES_GRAPHIQUE, DATA_DIR
from src.fonctions import lire_jours_actifs, lire_jours_donnees
from src.database import initialiser_base, lire_donnees_selectionnees, charger_csvs_par_batch
from src.graphique import CanvasGraphique
from synthese import generer_synthese, charger_donnees_periode
from typing import Optional, Set
import logging
logger = logging.getLogger(__name__)

# --- CLASSE POUR LA SELECTION DES COLONNES ---
class PageSelectionColonnes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        label = QLabel("Sélectionnez les données à afficher :")
        layout.addWidget(label)

        # Quelques cases à cocher (exemple)
        self.checkbox_temp = QPushButton("Température chaudière")
        self.checkbox_consigne = QPushButton("Consigne ECS")
        layout.addWidget(self.checkbox_temp)
        layout.addWidget(self.checkbox_consigne)

        # Bouton pour afficher le graphique (à relier plus tard)
        self.bouton_afficher = QPushButton("Afficher le graphique")
        layout.addWidget(self.bouton_afficher)


# --- CLASSE PRINCIPALE DE LA FENÊTRE ---
class FenetrePrincipale(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon interface")
        self.resize(400, 300)

        # --- Attributs de sélection ---
        self.date_debut: Optional[QDate] = None
        self.date_fin: Optional[QDate] = None

        # --- Jours actifs (chauffage / données) ---
        self.jours_actifs: Set[str] = set()
        self.jours_donnees: Set[str] = set()

        # Création du layout principal
        layout_principal = QVBoxLayout(self)

        # QStackedWidget qui contiendra les différentes pages (stack)
        self.stacked_widget = QStackedWidget()
        layout_principal.addWidget(self.stacked_widget)


        # --- Page 1 : sélection calendrier ---
        self.page_calendrier = QWidget()
        layout_calendrier = QVBoxLayout(self.page_calendrier)
        self.stacked_widget.addWidget(self.page_calendrier)

        # --- Page 2 : sélection des colonnes (checkbox) ---
        self.page_selection = QWidget()
        layout_selection = QVBoxLayout(self.page_selection)
        self.label_info_selection = QLabel("🔧 (future sélection de colonnes ici)")
        layout_selection.addWidget(self.label_info_selection)
        self.stacked_widget.addWidget(self.page_selection)

        # --- Page 3 : présentation des données ---
        self.page_graphique = QWidget()
        self.layout_graphique = QVBoxLayout(self.page_graphique)
        self.stacked_widget.addWidget(self.page_graphique)

        # Créer le canvas une seule fois et l’ajouter au layout page_graphique
        self.canvas_graphique = CanvasGraphique(self.page_graphique)
        self.layout_graphique.addWidget(self.canvas_graphique)

        # zone de texte pour la synthèse
        self.label_synthese = QTextEdit()
        self.label_synthese.setReadOnly(True)
        self.label_synthese.setStyleSheet("background-color: #f5f5f5;")
        self.layout_graphique.addWidget(self.label_synthese)


        # --- Zone de mise à jour base + barre ---
        self.bouton_maj = QPushButton("Mettre à jour la base de données")
        self.bouton_maj.clicked.connect(self.mettre_a_jour_base)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)

        self.zone_maj = QVBoxLayout()
        self.zone_maj.addWidget(self.bouton_maj)
        self.zone_maj.addWidget(self.progress_bar)

        layout_calendrier.addLayout(self.zone_maj)  # bouton + barre
        self.label_maj = QLabel("")
        layout_calendrier.addWidget(self.label_maj)  # message d’état


        # --- Choix entre date unique ou intervalle ---
        self.radio_unique = QRadioButton("Date unique")
        self.radio_intervalle = QRadioButton("Intervalle")
        self.radio_unique.setChecked(True)

        groupe_radio = QButtonGroup(self)
        groupe_radio.addButton(self.radio_unique)
        groupe_radio.addButton(self.radio_intervalle)

        ligne_radios = QHBoxLayout()
        ligne_radios.addWidget(self.radio_unique)
        ligne_radios.addWidget(self.radio_intervalle)
        layout_calendrier.addLayout(ligne_radios)


        # Création du widget calendrier
        self.calendrier = QCalendarWidget()
        self.calendrier.setGridVisible(True)
        self.calendrier.clicked.connect(self.date_selectionnee)
        layout_calendrier.addWidget(self.calendrier)

        # --- Zone d'affichage dynamique des dates sélectionnées ---
        self.label_selection = QLabel("Date sélectionnée :")
        layout_calendrier.addWidget(self.label_selection)   

        # --- Bouton de validation de la date ---
        self.bouton_valider = QPushButton("Valider la sélection")
        self.bouton_valider.clicked.connect(self.valider_selection)
        layout_calendrier.addWidget(self.bouton_valider)
     
        

        # Charger et colorer les jours actifs
        self.jours_actifs = lire_jours_actifs(DB_FILE)
        self.jours_donnees = lire_jours_donnees(DB_FILE)
        self.mettre_a_jour_calendrier()

        # Légende
        legende = QLabel()
        legende.setText(
            "<b>Légende :</b><br>"
            "<span style='background-color: lightgreen;'>&nbsp;&nbsp;&nbsp;&nbsp;</span> : Chauffage actif<br>"
            "<span style='color: blue;'>Texte bleu</span> : Présence de données"
        )
        layout_calendrier.addWidget(legende)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #e8e8e8;")
        self.log_output.setFixedHeight(100)
        layout_principal.addWidget(self.log_output)

        # --- Logger redirigé vers la zone de log ---
        log_handler = QTextEditLogger(self.log_output)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.addHandler(log_handler)

    def mettre_a_jour_calendrier(self):
        self.calendrier.setDateTextFormat(QDate(), QTextCharFormat())  # Reset

        format_donnees = QTextCharFormat()
        format_donnees.setForeground(QColor("blue"))  # Pour les jours avec données

        format_chauffage = QTextCharFormat()
        format_chauffage.setBackground(QColor("lightgreen"))  # Chauffage actif

        # Appliquer les jours avec données
        for jour_str in self.jours_donnees:
            qdate = QDate.fromString(jour_str, "yyyy-MM-dd")
            if qdate.isValid():
                self.calendrier.setDateTextFormat(qdate, format_donnees)

        # Appliquer les jours avec chauffage (ajoute la couleur de fond)
        for jour_str in self.jours_actifs:
            qdate = QDate.fromString(jour_str, "yyyy-MM-dd")
            if qdate.isValid():
                fmt = self.calendrier.dateTextFormat(qdate)
                fmt.setBackground(QColor("lightgreen"))  # Fusionne avec texte bleu
                self.calendrier.setDateTextFormat(qdate, fmt)

    def mettre_a_jour_base(self):
        self.label_maj.setText("⏳ Mise à jour en cours...")
        QApplication.processEvents()

        try:
            fichiers_csv = list(DATA_DIR.glob("*.csv"))
            total = len(fichiers_csv)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)

            def maj_progress(val):
                self.progress_bar.setValue(val)
                QApplication.processEvents()

            # 🟢 Appel avec barre de progression
            df = charger_csvs_par_batch(update_progress_callback=maj_progress)

            # Tu appelles ici ta fonction pour créer la base
            initialiser_base(df)

            QMessageBox.information(self, "Mise à jour", "Base mise à jour avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
        finally:
            self.progress_bar.setVisible(False)
            self.label_maj.setText("")

    def valider_selection(self):
        if self.radio_unique.isChecked():
            date_str = self.calendrier.selectedDate().toString("yyyy-MM-dd")
            logger.info(f"→ Date validée :{date_str}")
            self.stacked_widget.setCurrentWidget(self.page_selection)
        else:
            if self.date_debut and self.date_fin:
                logger.info("→ Intervalle validé : %s → %s", self.date_debut.toString("yyyy-MM-dd"), self.date_fin.toString("yyyy-MM-dd"))
                self.stacked_widget.setCurrentWidget(self.page_selection)
            else:
                logger.info("⚠️ Sélection d'intervalle incomplète.")


        # ✅ Créer les cases à cocher AVANT de changer de page
        colonnes = COLONNES_GRAPHIQUE
        self.creer_cases_a_cocher(colonnes)

        

        # ✅ Afficher la page 2 avec les checkboxes
        self.stacked_widget.setCurrentWidget(self.page_selection)

    def date_selectionnee(self, date: QDate):
        if self.radio_unique.isChecked():
            self.label_selection.setText(f"Date sélectionnée : {date.toString('yyyy-MM-dd')}")
        else:
            if not self.date_debut or (self.date_debut and self.date_fin):
                self.date_debut = date
                self.date_fin = None
                self.label_selection.setText(f"Début de l'intervalle : {self.date_debut.toString('yyyy-MM-dd')}")
            else:
                self.date_fin = date
                if self.date_fin < self.date_debut:
                    self.date_debut, self.date_fin = self.date_fin, self.date_debut
                self.label_selection.setText(
                    f"Intervalle : {self.date_debut.toString('yyyy-MM-dd')} → {self.date_fin.toString('yyyy-MM-dd')}"
                    )

    def creer_cases_a_cocher(self, colonnes):
        layout_selection = self.page_selection.layout()

        # Nettoyer le layout précédent
        for i in reversed(range(layout_selection.count())):
            widget = layout_selection.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 1. 📅 Afficher la date ou l'intervalle sélectionné
        if self.radio_unique.isChecked():
            date_str = self.calendrier.selectedDate().toString("yyyy-MM-dd")
            texte_info = f"📅 Date sélectionnée : {date_str}"
        else:
            if self.date_debut and self.date_fin:
                d1 = self.date_debut.toString("yyyy-MM-dd")
                d2 = self.date_fin.toString("yyyy-MM-dd")
                texte_info = f"📅 Intervalle sélectionné : {d1} → {d2}"
            else:
                texte_info = "❌ Aucune date sélectionnée"
        label_date = QLabel(texte_info)
        layout_selection.addWidget(label_date)

        # 2. 🧩 Ligne avec texte + bouton retour
        ligne_haut = QHBoxLayout()
        ligne_haut.addWidget(QLabel("🧩 Sélectionner les colonnes à afficher"))
        bouton_retour = QPushButton("⬅️ Retour")
        bouton_retour.clicked.connect(self.revenir_calendrier)
        ligne_haut.addWidget(bouton_retour)
        ligne_haut.addStretch()
        layout_selection.addLayout(ligne_haut)

        # 3. ✅ Cases à cocher sur plusieurs colonnes dans une zone scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout_selection.addWidget(scroll)

        # Widget conteneur dans le scroll
        conteneur = QWidget()
        scroll.setWidget(conteneur)

        # 🔢 Déterminer dynamiquement le nombre de colonnes
        total = len(colonnes)
        if total <= 20:
            nb_colonnes = 2
        elif total <= 40:
            nb_colonnes = 3
        elif total <= 60:
            nb_colonnes = 4
        else:
            nb_colonnes = 5

        # 🧱 GridLayout pour organiser les cases sur plusieurs colonnes
        grid = QGridLayout(conteneur)

        self.checkboxes = []
        for index, col in enumerate(colonnes):
            checkbox = QCheckBox(col)
            self.checkboxes.append(checkbox)
            row = index // nb_colonnes
            col_pos = index % nb_colonnes
            grid.addWidget(checkbox, row, col_pos)

        # 4. 📥 Boutons "Tout décocher" et "Valider"
        ligne_boutons = QHBoxLayout()

        bouton_decocher = QPushButton("🗑️ Tout décocher")
        bouton_decocher.clicked.connect(self.tout_decocher)

        bouton_valider = QPushButton("✅ Valider la sélection")
        bouton_valider.clicked.connect(self.valider_colonnes)

        ligne_boutons.addWidget(bouton_decocher)
        ligne_boutons.addStretch()
        ligne_boutons.addWidget(bouton_valider)

        layout_selection.addLayout(ligne_boutons)


        # 5. 📐 Ajuster la largeur minimale de la fenêtre
        largeur_min = nb_colonnes * 200  # Ajuster si besoin
        self.setMinimumWidth(largeur_min)
        self.resize(self.sizeHint())
        def revenir_calendrier(self):
            self.stacked_widget.setCurrentWidget(self.page_calendrier)

    def tout_decocher(self):
        for cb in self.checkboxes:
            cb.setChecked(False)

    def revenir_calendrier(self):
        self.stacked_widget.setCurrentWidget(self.page_calendrier)

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

        # --- Gestion spécifique de 'ecs_etat' ---
        tracer_ecs_etat = "ecs_etat" in colonnes_selectionnees
        if tracer_ecs_etat:
            colonnes_selectionnees.remove("ecs_etat")  # On ne veut pas tracer la courbe brute

        colonnes_avec_datetime = colonnes_selectionnees + ["datetime"]
        if tracer_ecs_etat:
            colonnes_avec_datetime.append("ecs_etat")  # colonne brute

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
        
        # --- Nettoyer page graphique avant d’ajouter ---
        for i in reversed(range(self.layout_graphique.count())):
            widget = self.layout_graphique.itemAt(i).widget()
            if widget and widget != self.canvas_graphique:
                widget.setParent(None)
        if not df.empty:
            # --- Ajouter le graphique ---
            # --- Tracer les données classiques ---
            if colonnes_selectionnees:
                self.canvas_graphique.tracer_donnees(df[["datetime"] + colonnes_selectionnees])

            # --- Tracer état ECS en arrière-plan ---
            if tracer_ecs_etat:
                self.canvas_graphique.tracer_ecs_etat_zones(df[["datetime", "ecs_etat"]])

        
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

class QTextEditLogger(logging.Handler, QObject):
    log_signal = pyqtSignal(str)

    def __init__(self, text_edit):
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.text_edit = text_edit
        self.log_signal.connect(self._append_text)

    def emit(self, record):
        msg = self.format(record)
        self.log_signal.emit(msg)

    def _append_text(self, msg):
        self.text_edit.append(msg)



# --- POINT D’ENTRÉE ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec_())
