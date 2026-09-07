# Tontine Hero — Gestion de Tontines et Finances Personnelles

Application web moderne pour gerer ses cercles de tontine, suivre son budget, atteindre ses objectifs d'epargne et simuler des cagnottes.

Construite avec Python (FastAPI) et SQLite, elle fonctionne 100% en local sans aucune dependance cloud.

---

## Fonctionnalites

- **Gestion des tontines** : suivi des tours de table, beneficiaire du tour, pointage des cotisations, boutons WhatsApp de recu et de rappel
- **Budget et portefeuille** : suivi des entrees, des depenses et de l'argent alloue aux tontines par categorie
- **Objectifs d'epargne** : tirelires avec barre de progression en temps reel
- **Simulateur** : estimation des cagnottes selon la duree et conseils de positionnement (debut/milieu/fin de cycle)
- **Score de serenite** : indicateur de sante financiere calcule dynamiquement
- **Multi-devises** : FCFA (XOF), EUR, USD, GNF
- **Responsive** : adapte pour PC et mobile (bottom nav sur mobile, sidebar nav sur desktop)

---

## Stack technique

| Composant | Technologie |
|-----------|------------|
| Backend | Python 3.12, FastAPI, Uvicorn |
| Templates | Jinja2 (server-side rendering) |
| Base de donnees | SQLite (locale, zero config) |
| Frontend | HTML/CSS custom, responsive, dark theme |
| Typographie | Inter (Google Fonts) |

---

## Installation et lancement

### 1. Cloner le projet
```bash
git clone https://github.com/primemarafa/tontine-hero.git
cd tontine-hero
```

### 2. Creer un environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate    # Windows
# ou : source venv/bin/activate  # Linux/Mac
```

### 3. Installer les dependances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application
```bash
uvicorn app.main:app --reload --port 8000
```

Ouvrir http://localhost:8000 dans le navigateur.

La base de donnees SQLite est creee automatiquement au premier lancement avec des donnees de demonstration.

---

## Structure du projet

```
tontine-hero/
|-- app/
|   |-- main.py          # Routes FastAPI (dashboard, tontines, budget, epargne, simulateur)
|   |-- models.py        # Fonctions metier (profil, tontines, transactions, score)
|   +-- database.py      # Connexion SQLite, schema, donnees initiales
|
|-- templates/
|   |-- base.html        # Layout principal (header, nav, modales)
|   |-- dashboard.html   # Tableau de bord
|   |-- tontines.html    # Gestion des cercles de tontine
|   |-- budget.html      # Budget et depenses
|   |-- savings.html     # Objectifs d'epargne
|   +-- simulator.html   # Simulateur de cagnottes
|
|-- static/
|   +-- styles.css       # Styles (dark theme, responsive, fintech design)
|
|-- requirements.txt     # Dependances Python
|-- LICENSE              # Licence MIT
+-- .gitignore
```

---

## Licence

MIT — voir [LICENSE](LICENSE)
