# 🔥 Projet Okofen - Analyse de Données Chaudière

Ce projet permet de charger, structurer et analyser les données issues d'une chaudière à granulés **Okofen**, grâce à une base de données SQLite et divers outils Python.

la chaudière emet un fichier csv par jour contenant une cinquantaine de mesure relevée toutes les minutes.

le programme créer une base de données et génere graphiqe et synthèse en fonction des dates choisies. 

## 📁 Structure du projet

```
okofen/
├── data/                   # Données brutes : tous les fichiers CSV.
│   └── *.csv
│   └── chaudiere.sqlite    # Base de données SQLite créée depuis les CSV.
│
├── src/                    # Code source principal.
│   ├── config.py           # Chemins, constantes, dictionnaires de renommage.
│   ├── database.py         # Création et manipulation de la base SQLite.
│   ├── fonction.py         # Outils d’analyse et d’exploitation des données.
│   ├── main.py             # Script principal pour orchestrer la base et les analyses.
│   ├── verif_data.py       # Vérification format et cohérence des CSV.
│   ├── grahique.py         # Création de graphique.
│   ├── interface.py        # Interface utilisateur.
│   ├── synthese.py         # structure de l'interface.


├── README.md               # Explication du projet.
```


## ⚙️ Fonctionnement

1. **Importer les CSV** : placer les fichiers `.csv` de la chaudière dans le dossier `data/`.
2. **Créer la base** : lancer `main.py` pour générer automatiquement la base SQLite.
3. **Analyser les données** : utiliser les fonctions de `fonctions.py` pour extraire, lisser ou visualiser les données.
4. **Générer des graphiques** utilisation de matplotlib `visualisation.py` pour présenter visuellement les données
5. **Utiliser une interface graphique** création d'une interface `interface.py`avec PyQt5 pour simplifier l'utilisation

## 🚧 Objectifs futurs

- Exportation des rapports automatisés
- Détection automatique d’erreurs ou d’anomalies dans les données
- optimisation du fonctionnement et des temps de chargement

## ✅ Dépendances

Ce projet nécessite Python 3 et les bibliothèques suivantes :

- `pandas`
- `sqlite3` (standard)
- `matplotlib` 
- `PyQt5` 



