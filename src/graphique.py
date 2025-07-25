
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sqlite3
from src.config import DB_FILE, STYLE_COLONNE, RANGE_LIMITS, ecs_etat_label, chauffage1_label
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
from matplotlib.patches import Polygon, Patch
from matplotlib.colors import to_rgba
import numpy as np
import logging
logger = logging.getLogger(__name__)



# --- CLASSE POUR LA GÉNÉRATION DE GRAPHIQUE ---
class CanvasGraphique(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 6))
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)


    '''       
    def tracer_donnees(self, df, colonnes):
        self.axes.clear()
        for col in colonnes:
            if col in df.columns:
                self.axes.plot(df["datetime"], df[col], label=col)
        
        self.axes.legend()
        self.draw()
    '''
    def tracer_courbes(self, df, zones=True):
        self.fig.clear()
        ax_middle = self.fig.add_subplot(111)
        self.axes = ax_middle  # pour compatibilité

        ax_low = ax_middle.twinx()
        ax_high = ax_middle.twinx()

        axes_dict = {
            "low": ax_low,
            "middle": ax_middle,
            "high": ax_high,
            "state": ax_middle,
        }
        used_axes = set()

        if df.empty:
            ax_middle.text(0.5, 0.5, "📭 Aucune donnée à afficher", ha="center", va="center")
            self.draw()
            return

        df = df.copy()

        # S'assurer que "datetime" est bien une colonne utilisable pour l'index
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
            df.set_index("datetime", inplace=True)

        # Vérification obligatoire : on ne continue que si l’index est bien un DatetimeIndex
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("Le DataFrame doit être indexé par un DatetimeIndex.")


        for col in df.columns:
            if col.lower() in ("tick_label", "date", "heure"):
                continue

            style = STYLE_COLONNE.get(col, {"type": "line", "color": "black"})
            plot_type = style.get("type", "line")
            color = style.get("color", "black")
            linewidth = style.get("linewidth", 1.5)
            range_type = style.get("range", "middle")
            ax = axes_dict.get(range_type, ax_middle)

            valeurs = df[col]
            if range_type == "low" and valeurs.max() > 1:
                valeurs = valeurs / 100

            serie_propre = valeurs.dropna()

            if serie_propre.empty:
                continue

            if plot_type == "zone":
                self.tracer_zone_etats_multiples(df, col, style)
                continue

            if plot_type == "line":
                ax.plot(serie_propre.index, serie_propre.values, label=col, color=color, linewidth=linewidth)
            elif plot_type == "step":
                ax.step(serie_propre.index, serie_propre.values, label=col, color=color, where="post", linewidth=linewidth)
            elif plot_type == "bar":
                ax.bar(serie_propre.index, serie_propre.values, label=col, color=color)
            else:
                ax.plot(serie_propre.index, serie_propre.values, label=col, color=color, linewidth=linewidth)

            used_axes.add(range_type)

        # Format X : heures et dates
        ax_middle.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
        ax_middle.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
        ax_middle.tick_params(axis='x', which='major', labelsize=8, direction='out', pad=7)

        ax2 = ax_middle.axes.secondary_xaxis('bottom')
        ax2.get_xaxis().set_major_locator(mdates.DayLocator())
        ax2.get_xaxis().set_major_formatter(mdates.DateFormatter('%d-%m'))
        ax2.get_xaxis().set_tick_params(labelsize=10, pad=15)

        # Axe Y : style
        ax_middle.set_ylabel("Valeurs")
        ax_middle.set_xlabel("")

        ax_low.spines["left"].set_position(("axes", -0.1))
        ax_low.yaxis.set_label_position("left")
        ax_low.yaxis.set_ticks_position("left")

        ax_high.spines["right"].set_position(("axes", 1.1))
        ax_high.yaxis.set_label_position("right")
        ax_high.yaxis.set_ticks_position("right")

        # Appliquer les limites d’axes
        for range_key in used_axes:
            ax = axes_dict[range_key]
            limits = RANGE_LIMITS.get(range_key)
            if limits:
                margin = (limits[1] - limits[0]) * 0.05
                ax.set_ylim(limits[0] - margin, limits[1] + margin)

        # Récupérer les handles/labels des courbes déjà tracées
        courbe_handles, courbe_labels = ax.get_legend_handles_labels()

        # Groupes de légendes pour les zones
        ecs_patches = []
        chauffage_patches = []

        for col in ("ecs_etat", "chauffage1_etat"):
            if col not in df.columns:
                 continue
            style = STYLE_COLONNE.get(col)
            if not style or style.get("type") != "zone":
                continue

            etats_couleurs = style.get("etats", {})

            # Choix fonction de label
            get_label = ecs_etat_label if col == "ecs_etat" else chauffage1_label

            for etat_valeur, couleur in etats_couleurs.items():
                if isinstance(couleur, str) and couleur.lower().endswith("00"):
                    continue
                if etat_valeur == "__default__":
                    continue

                label = get_label(etat_valeur)
                patch = Patch(color=couleur, alpha=style.get("alpha", 0.5), label=label)
                if col == "ecs_etat":
                    ecs_patches.append(patch)
                else:
                    chauffage_patches.append(patch)

        # --- Affichage de 3 légendes séparées ---
        def group_with_title(title, patches):
            """Crée les patches et labels avec titre"""
            handles = patches
            labels = [p.get_label() for p in patches]
            return handles, labels, title

        courbe_h, courbe_l, courbe_title = courbe_handles, courbe_labels, "Courbes"
        ecs_h, ecs_l, ecs_title = group_with_title("ecs_etat", ecs_patches)
        chauf_h, chauf_l, chauf_title = group_with_title("chauffage1_etat", chauffage_patches)

        # Zones de légende personnalisées sous le graphe
        leg1 = self.fig.add_axes([0.05, 0.08, 0.25, 0.15])
        leg1.axis("off")
        leg1.legend(courbe_h, courbe_l, title=courbe_title, loc="upper left", frameon=False)

        if ecs_h:
            leg2 = self.fig.add_axes([0.38, 0.08, 0.25, 0.15])
            leg2.axis("off")
            leg2.legend(ecs_h, ecs_l, title=ecs_title, loc="upper left", frameon=False)

        if chauf_h:
            leg3 = self.fig.add_axes([0.70, 0.08, 0.25, 0.15])
            leg3.axis("off")
            leg3.legend(chauf_h, chauf_l, title=chauf_title, loc="upper left", frameon=False)

        self.fig.subplots_adjust(bottom=0.35)


        if not df.empty:
            debut = df.index.min()
            fin = df.index.max()
            if (fin - debut) < pd.Timedelta(hours=24):
                fin = debut + pd.Timedelta(hours=24)
            ax_middle.set_xlim(debut, fin)
            
        self.draw()




    def tracer_zone_etats_multiples(self, df, col, meta):
    
        ax = self.figure.gca()
        alpha = meta.get("alpha", 0.4)
        direction = meta.get("gradient", "up")
        etats_couleurs = meta.get("etats", {})

        serie = df[col]

        # Repérer les changements successifs dans la série des labels
        groupe = (serie != serie.shift()).cumsum()

        for _, group in serie.groupby(groupe):
            etat = group.iloc[0]
            color = etats_couleurs.get(etat, "red")

            if isinstance(color, str) and color.lower().endswith("00"):  # ignorer totalement transparent
                continue

            start = group.index[0]
            end = group.index[-1]

            self.draw_gradient_band(ax, start, end, color=color, alpha=alpha, direction=direction, zorder=0)

        # Optionnel : ajuster les limites verticales pour que la zone soit visible
        #ax.set_ylim(0, 1)

    def draw_gradient_band(self, ax, start, end, color, alpha, direction, zorder=0):
            
            n = 100
            gradient = np.linspace(0, 1, n).reshape((n, 1))
            if direction == "down":
                gradient = gradient[::-1]

            rgba = mcolors.to_rgba(color, alpha=1)
            img = np.zeros((n, 1, 4))
            img[..., :3] = rgba[:3]
            img[..., 3] = gradient * alpha

            start_val = mdates.date2num(start)
            end_val = mdates.date2num(end)

            if start_val == end_val:
                start_val -= 0.0001  # petit ajustement pour éviter étendue nulle
                end_val += 0.0001

            ax.imshow(
                img,
                extent=(start_val, end_val, 0, 1),
                transform=ax.get_xaxis_transform(),
                aspect='auto',
                zorder=0
            )
