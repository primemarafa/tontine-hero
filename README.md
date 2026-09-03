# 🪙 Tontine Hero — Plateforme de Gestion de Tontines & Finances Réelles (Python Edition)

Application moderne, sobre et responsive pour gérer ses cercles de tontine, ses cotisations réelles, son budget personnel et ses objectifs d'épargne.

---

## 🚀 Fonctionnalités Clés

* **📱 Multi-Appareil (Responsive)** : Adapté pour grand écran PC et smartphone mobile.
* **🔄 Gestion des Tontines Réelles** : Suivi des tours de table, bénéficiaire du tour, pointage des cotisations et boutons WhatsApp 1-clic de reçu et de rappel.
* **💳 Budget & Portefeuille** : Suivi des entrées, des dépenses et de l'argent alloué aux tontines par catégorie.
* **🎯 Tirelires & Épargne** : Objectifs financiers personnels avec barre de progression en temps réel.
* **🧮 Simulateur & Stratégie** : Estimation des cagnottes selon la durée et conseils de positionnement (début/milieu/fin de cycle).
* **🔒 100% Local & Sécurisé** : Base de données SQLite locale sans dépendance cloud payante.

---

## 🛠️ Stack Technique

* **Backend** : Python 3.12+ / FastAPI / Uvicorn
* **Base de Données** : SQLite 3
* **Templates** : Jinja2
* **Frontend** : CSS3 Responsive (Dark Fintech Theme)

---

## 📦 Installation & Lancement

1. **Cloner le dépôt :**
   ```bash
   git clone <URL_DE_VOTRE_DEPOT>
   cd tontine-hero-python
   ```

2. **Créer l'environnement virtuel et installer les dépendances :**
   ```bash
   python -m venv venv
   # Sur Windows :
   .\venv\Scripts\activate
   # Sur Linux / macOS :
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Lancer le serveur :**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Ouvrir dans le navigateur :**
   * Sur PC : `http://localhost:8000/`
   * Sur smartphone (même Wi-Fi) : `http://<VOTRE_IP_LOCALE>:8000/`
