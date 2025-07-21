

from pathlib import Path
import logging 

# Dossier racine du projet (on part du fichier config.py dans src/)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Dossier des données
DATA_DIR = PROJECT_ROOT / "data"

# Chemin vers la base de données
DB_FILE = DATA_DIR / "ma_chaudiere.sqlite"

logging.basicConfig(
    level=logging.INFO,  # Tu peux passer à DEBUG pour plus de détails
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

#dictionnaire de traduction de nom de colonnes
RENAME_DICT = {
    'Datum' : 'date',
    'Zeit': 'heure',
    'AT [°C]': 'temperature_exterieur',
    'ATakt [°C]': 'temperature_actuelle',
    'PE1_BR1': 'entree_bruleur', #inutilisé
    'HK1 VL Ist[°C]': 'chauffage1_depart_mesure',
    'HK1 VL Soll[°C]': 'chauffage1_depart_consigne',
    'HK1 RT Ist[°C]': 'chauffage1_ambiance_mesure', #inutilisé
    'HK1 RT Soll[°C]': 'chauffage1_ambiance_consigne', #inutilisé
    'HK1 Pumpe': 'chauffage1_pompe',
    'HK1 Mischer': 'chauffage1_melangeur',
    'HK1 Fernb[°C]': 'chauffage1_telecommande', #inutilisé
    'HK1 Status': 'chauffage1_statut', #reduit actif, temp ext > lim T ext
    'WW1 EinT Ist[°C]': 'ecs_marche_mesure', #inutilisé, pour le bouclage ecs
    'WW1 AusT Ist[°C]': 'ecs_arret_mesure',
    'WW1 Soll[°C]': 'ecs_consigne',
    'WW1 Pumpe': 'ecs_pompe', #inutilisé, pour le bouclage ecs
    'WW1 Status': 'ecs_etat', #Off, T reduit atteinte
    'PE1 KT[°C]': 'chaudiere_temp_mesure',
    'PE1 KT_SOLL[°C]': 'chaudiere_temp_consigne',
    'PE1 UW Freigabe[°C]': 'chaudiere_uw_autorisation', #temporisation marche
    'PE1 Modulation[%]': 'modulation_puissance_chaudiere',
    'PE1 FRT Ist[°C]': 'flamme_mesure',
    'PE1 FRT Soll[°C]': 'flamme_consigne',
    'PE1 FRT End[°C]': 'flamme_finale_consigne',
    'PE1 Einschublaufzeit[zs]': 'vis_bruleur_marche',
    'PE1 Pausenzeit[zs]': 'vis_bruleur_tempo_arret',
    'PE1 Luefterdrehzahl[%]': 'vis_bruleur_tempo_marche', #inutilisé
    'PE1 Saugzugdrehzahl[%]': 'ventilateur_fumee', #ventilateur dépression foyer
    'PE1 Unterdruck Ist[EH]': 'depression_mesure', #dépression mesurée chambre de combustion
    'PE1 Unterdruck Soll[EH]': 'depression_consigne', #dépression consigne chambre de combustion
    'PE1 Fuellstand[kg]': 'reservoir_kg',
    'PE1 Fuellstand ZWB[kg]': 'reservoir_interne_kg',
    'PE1 Status': 'chaudiere_etat',
    'PE1 Motor ES': 'vis_bruleur', #ecluse pare feu
    'PE1 Motor RA': 'moteur_ra', # vis du silo
    'PE1 Motor RES1': 'moteur_res1', #resistance d'allumage
    'PE1 Motor TURBINE': 'moteur_turbine', #turbine d'aspiration pellets
    'PE1 Motor ZUEND': 'moteur_allumage',
    'PE1 Motor UW[%]': 'moteur_uw', #inutilisé
    'PE1 Motor AV': 'moteur_avance_pellet', #vis d'allimentation du foyer
    'PE1 Motor RES2': 'moteur_res2', #resistance 2
    'PE1 Motor MA': 'moteur_ma', 
    'PE1 Motor RM': 'moteur_rm', #ramonage
    'PE1 Motor SM': 'moteur_sm', #inutilisé
    'PE1 Res1 Temp.[°C]': 'temperature_res1', #resistaance 1
    'PE1 Res2 Temp.[°C]': 'temperature_res2', #resistance 2
    'PE1 CAP RA': 'capteur_ra', #détection pellet ecluse pare feu
    'PE1 CAP ZB': 'capteur_zb', #capteur trémie interne (niveau haut)
    'PE1 AK': 'capteur_ak', #inutilisé
    'PE1 Saug-Int[min]': 'intervalle_aspiration_min',
    'PE1 DigIn1': 'entree_numerique_1',
    'PE1 DigIn2': 'entree_numerique_2',
    'Fehler1': 'erreur1',
    'Fehler2': 'erreur2',
    'Fehler3': 'erreur3',
    'Unnamed: 56': 'colonne_inconnue_56'
}

COLONNES_GRAPHIQUE = [
    'temperature_exterieur',
    'temperature_actuelle',
    'chauffage1_depart_mesure',
    'chauffage1_depart_consigne',
    'chauffage1_pompe',
    'chauffage1_melangeur',
    'chauffage1_statut',
    'ecs_marche_mesure',
    'ecs_arret_mesure',
    'ecs_consigne',
    'ecs_pompe',
    'ecs_etat',
    'chaudiere_temp_mesure',
    'chaudiere_temp_consigne',
    'chaudiere_uw_autorisation',
    'modulation_puissance_chaudiere',
    'flamme_mesure',
    'flamme_consigne',
    'flamme_finale_consigne',
    'vis_bruleur_marche',
    'vis_bruleur_tempo_arret',
    'vis_bruleur_tempo_marche',
    'ventilateur_fumee',
    'depression_mesure',
    'reservoir_kg',
    'reservoir_interne_kg',
    'chaudiere_etat',
    'vis_bruleur',
    'moteur_ra',
    'moteur_res1',
    'moteur_turbine',
    'moteur_allumage',
    'moteur_uw',
    'moteur_avance_pellet',
    'moteur_res2',
    'moteur_ma',
    'moteur_rm',
    'moteur_sm',
    'temperature_res1',
    'temperature_res2',
    'capteur_ra',
    'capteur_zb',
    'capteur_ak',
    'intervalle_aspiration_min'
]

'''
 Signification des champs :
    type : Type de tracé :
        "line" : ligne continue (valeurs analogiques)
        "step" : ligne en escalier (états ON/OFF)
        "bar" : histogramme vertical (quantités)
    color : Couleur du tracé (nom matplotlib ou code hexadécimal, ex. "blue", "#00FF00")
    ylabel : Unité ou description affichée sur l’axe Y si utilisé seul ou dédié
    range : Catégorie d’échelle pour grouper les courbes sur différents axes Y :
        "low" → valeurs binaires (0–1)
        "middle" → températures courantes (env. -20°C à +100°C)
        "high" → valeurs élevées (modulation %, flamme, kg, etc.)
    linewidth (optionnel) : Épaisseur du trait (par défaut : 1.5)
    marker (optionnel) : Forme du marqueur sur les points (ex. "o" pour rond, "^" pour triangle)
    
    {
    "type":"",
    "color":"",
    "ylabel":"",
    "range":"",
    "linewidth":"",
    "marker":""
    }
'''

RANGE_LIMITS = {
    "low": (0, 1.1),
    "middle": (-20, 100),
    "high": (0, 1000),
}

def ecs_etat_label(val):
    """
    Retourne un label lisible pour les codes de statut ECS.
    """
    if isinstance(val, int):
        if val == 8200:
            return "off"
        elif val == 16912:
            return "preparation"
        elif val == 8208:
            return "confort"
        else:
            return f"inconnu ({val})"
    elif isinstance(val, str):
        return val
    else:
        return "inconnu"
    
def chauffage1_label(val):
    """
    Retourne un label lisible pour les codes de statut chauffage1.
    """
    if isinstance(val, int):
        if val == 0:
            return "off"
        elif val == 16:
            return "reduit"
        elif val == 32:
            return "confort"
        elif val == 1056:
            return "mode 1"
        elif val == 2097184:
            return "mode 2"
        else:
            return f"inconnu ({val})"
    elif isinstance(val, str):
        return val
    else:
        return "inconnu"
    
        
STYLE_COLONNE = {
    "temperature_exterieur": {
        "type": "line",                             # Type de courbe "line" | "step" | "bar"
        "color": "#1f77b4",                            # Couleur matplotlib (nom ou hexadécimal)
        "ylabel": "Température extérieur (°C)",     # Étiquette de l’axe Y (facultatif mais conseillé)
        "range": "middle",                          # Gamme de valeurs (pour définir l’axe Y) low, middle, high
        "linewidth": 1.5,                           # Épaisseur du trait (facultatif)
        "marker": "o"                               # Marqueur sur les points (facultatif)"o" | "^" | None
    },
        "temperature_actuelle": {
        "type": "line",
        "color": "#ff7f0e",
        "ylabel": "Température actuelle (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "chauffage1_depart_mesure": {
        "type": "line",
        "color": "#2ca02c",
        "ylabel": "Départ mesuré chauffage (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "chauffage1_depart_consigne": {
        "type": "line",
        "color": "#d62728",
        "ylabel": "Consigne départ chauffage (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "chauffage1_pompe": {
        "type": "step",
        "color": "#9467bd",
        "ylabel": "Pompe chauffage (0/100)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "chauffage1_melangeur": {
        "type": "line",
        "color": "#8c564b",
        "ylabel": "Mélangeur chauffage (%)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "ecs_marche_mesure": {
        "type": "step",
        "color": "#7f7f7f",
        "ylabel": "Marche ECS (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "ecs_arret_mesure": {
        "type": "step",
        "color": "#bcbd22",
        "ylabel": "Arrêt ECS (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "ecs_consigne": {
        "type": "line",
        "color": "#17becf",
        "ylabel": "Température consigne ECS (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": "o"
    },
    "ecs_pompe": {
        "type": "step",
        "color": "#1f77b4",
        "ylabel": "Pompe ECS (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "chaudiere_temp_mesure": {
        "type": "line",
        "color": "#2ca02c",
        "ylabel": "Température chaudière (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "chaudiere_temp_consigne": {
        "type": "line",
        "color": "#d62728",
        "ylabel": "Consigne chaudière (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "chaudiere_uw_autorisation": {
        "type": "step",
        "color": "#9467bd",
        "ylabel": "Autorisation UW (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "modulation_puissance_chaudiere": {
        "type": "line",
        "color": "#8c564b",
        "ylabel": "Modulation puissance (%)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "flamme_mesure": {
        "type": "line",
        "color": "#e377c2",
        "ylabel": "Flamme mesurée",
        "range": "high",
        "linewidth": 1.5,
        "marker": None
    },
    "flamme_consigne": {
        "type": "line",
        "color": "#7f7f7f",
        "ylabel": "Consigne flamme",
        "range": "high",
        "linewidth": 1.5,
        "marker": None
    },
    "flamme_finale_consigne": {
        "type": "line",
        "color": "#bcbd22",
        "ylabel": "Consigne finale flamme",
        "range": "high",
        "linewidth": 1.5,
        "marker": None
    },
    "vis_bruleur_marche": {
        "type": "step",
        "color": "#17becf",
        "ylabel": "Vis brûleur marche (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "vis_bruleur_tempo_arret": {
        "type": "step",
        "color": "#1f77b4",
        "ylabel": "Tempo arrêt vis (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "vis_bruleur_tempo_marche": {
        "type": "step",
        "color": "#ff7f0e",
        "ylabel": "Tempo marche vis (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "ventilateur_fumee": {
        "type": "line",
        "color": "#2ca02c",
        "ylabel": "Ventilateur fumée (%)",
        "range": "high",
        "linewidth": 1.5,
        "marker": None
    },
    "depression_mesure": {
        "type": "line",
        "color": "#d62728",
        "ylabel": "Dépression mesurée",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "reservoir_kg": {
        "type": "line",
        "color": "#9467bd",
        "ylabel": "Réservoir principal (kg)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "reservoir_interne_kg": {
        "type": "line",
        "color": "#8c564b",
        "ylabel": "Réservoir interne (kg)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "chaudiere_etat": {
        "type": "step",
        "color": "#e377c2",
        "ylabel": "État chaudière (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "vis_bruleur": {
        "type": "step",
        "color": "#7f7f7f",
        "ylabel": "Vis brûleur (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_ra": {
        "type": "step",
        "color": "#bcbd22",
        "ylabel": "Moteur RA (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_res1": {
        "type": "step",
        "color": "#17becf",
        "ylabel": "Moteur RES1 (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_turbine": {
        "type": "step",
        "color": "#1f77b4",
        "ylabel": "Moteur turbine (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_allumage": {
        "type": "step",
        "color": "#ff7f0e",
        "ylabel": "Allumage moteur (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_uw": {
        "type": "step",
        "color": "#2ca02c",
        "ylabel": "Moteur UW (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_avance_pellet": {
        "type": "step",
        "color": "#d62728",
        "ylabel": "Avance pellet (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_res2": {
        "type": "step",
        "color": "#9467bd",
        "ylabel": "Moteur RES2 (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_ma": {
        "type": "step",
        "color": "#8c564b",
        "ylabel": "Moteur MA (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_rm": {
        "type": "step",
        "color": "#e377c2",
        "ylabel": "Moteur RM (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "moteur_sm": {
        "type": "step",
        "color": "#7f7f7f",
        "ylabel": "Moteur SM (0/1)",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "temperature_res1": {
        "type": "line",
        "color": "#bcbd22",
        "ylabel": "Température RES1 (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "temperature_res2": {
        "type": "line",
        "color": "#17becf",
        "ylabel": "Température RES2 (°C)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "capteur_ra": {
        "type": "line",
        "color": "#1f77b4",
        "ylabel": "Capteur RA",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "capteur_zb": {
        "type": "line",
        "color": "#ff7f0e",
        "ylabel": "Capteur ZB",
        "range": "low",
        "linewidth": 1.5,
        "marker": None
    },
    "capteur_ak": {
        "type": "line",
        "color": "#2ca02c",
        "ylabel": "Capteur AK",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    },
    "intervalle_aspiration_min": {
        "type": "line",
        "color": "#d62728",
        "ylabel": "Intervalle aspiration (min)",
        "range": "middle",
        "linewidth": 1.5,
        "marker": None
    }
        }