
import sys
from pathlib import Path

# Ajoute le dossier parent (racine 'okofen') au path Python
sys.path.append(str(Path(__file__).resolve().parents[1]))
import sqlite3
from src.config import DB_FILE, STYLE_COLONNE, RANGE_LIMITS
import matplotlib.dates as mdates
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt



# --- CLASSE POUR LA GÉNÉRATION DE GRAPHIQUE ---
class CanvasGraphique(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(12, 6))
        super().__init__(self.fig)
        self.setParent(parent)
        self.axes = self.fig.add_subplot(111)


        
    def tracer_donnees(self, df):
        self.fig.clear()
        ax_middle = self.fig.add_subplot(111)
        self.axes = ax_middle  # pour compatibilité

        ax_low = ax_middle.twinx()
        ax_high = ax_middle.twinx()

        axes_dict = {
            "low": ax_low,
            "middle": ax_middle,
            "high": ax_high,
            }
        used_axes = set()



        if df.empty:
            ax_middle.text(0.5, 0.5, "📭 Aucune donnée à afficher", ha="center", va="center")
            self.draw()
            return

        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime")
       
        ylabels = set()  # Collecteur d'unités


        # Tracer chaque colonne sauf les techniques

        for col in df.columns:
            if col.lower() in ("tick_label", "date", "heure"):
                continue

            style = (STYLE_COLONNE or {}).get(col, {"type": "line", "color": "black"})
            plot_type = style.get("type", "line")
            color = style.get("color", "black")
            linewidth = style.get("linewidth", 1.5)
            marker = style.get("marker", None)
            range_type = style.get("range", "middle")  # NEW: middle par défaut
            ax = axes_dict.get(range_type, ax_middle)  # NEW: sélectionne l'axe en fonction

             # 🟨 Normalisation si axe "low" avec des données binaires 0/100
            valeurs = df[col]
            if range_type == "low" and valeurs.max() > 1:
                valeurs = valeurs / 100  # convertit 0/100 → 0/1 pour correspondre à l’échelle low

            if style["type"] == "line":
                ax.plot(df.index, valeurs, label=col, color=style["color"])
            elif style["type"] == "step":
                ax.step(df.index, valeurs, label=col, color=style["color"], where="post")
            elif style["type"] == "bar":
                ax.bar(df.index, valeurs, label=col, color=style["color"])
            else:
                ax.plot(df.index, valeurs, label=col, color=color, linewidth=linewidth)


            used_axes.add(range_type)


        # Axe X : heures en haut
        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))  # toutes les 3h
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
        ax.tick_params(axis='x', which='major', labelsize=8, direction='out', pad=7)

        # Axe secondaire en bas : date par jour
        ax2 = self.axes.secondary_xaxis('bottom')
        ax2.get_xaxis().set_major_locator(mdates.DayLocator())
        ax2.get_xaxis().set_major_formatter(mdates.DateFormatter('%d-%m'))
        ax2.get_xaxis().set_tick_params(labelsize=10, pad=15)


        ax_middle.set_ylabel("Valeurs")
        ax_middle.set_xlabel("")
        
        # Décale visuellement les axes secondaires
        ax_low.spines["left"].set_position(("axes", -0.1))
        ax_low.yaxis.set_label_position("left")
        ax_low.yaxis.set_ticks_position("left")

        ax_high.spines["right"].set_position(("axes", 1.1))
        ax_high.yaxis.set_label_position("right")
        ax_high.yaxis.set_ticks_position("right")

        # Légende combinée
        handles, labels = [], []
        for ax in (ax_low, ax_middle, ax_high):
            h, l = ax.get_legend_handles_labels()
            handles += h
            labels += l
        self.fig.legend(handles, labels, loc="lower center", ncol=3)
        self.fig.tight_layout(rect=[0, 0.05, 1, 1])  # laisse de la place pour la légende

        for range_key in used_axes:
            ax = axes_dict[range_key]
            limits = RANGE_LIMITS.get(range_key)
            if limits:
                margin = (limits[1] - limits[0]) * 0.05  # marge de 5% pour l’esthétique
                ax.set_ylim(limits[0] - margin, limits[1] + margin)

        self.draw()
