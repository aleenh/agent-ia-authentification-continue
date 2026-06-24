# agent_ia — Backend

Backend complet de l'agent IA : entraînement ML, moteur de scoring, boucle de surveillance continue, API REST et dashboard.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `scoring.py` | Charge les artefacts ML et expose `calculer_score`, `score_combine`, `decision_agent` |
| `agent.py` | Boucle continue (APScheduler, cycle de 30s), simulation d'attaque manuelle |
| `actions.py` | Actions adaptatives : envoi OTP par email (Gmail SMTP), blocage de carte |
| `api.py` | API REST FastAPI, 9 endpoints sécurisés par JWT, persistance PostgreSQL |
| `dashboard.py` | Dashboard Streamlit temps réel |
| `tests.py` | Tests et calcul des métriques FAR / FRR / EER |
| `populate_db.py` | Remplissage de la base PostgreSQL avec des transactions réelles du dataset |
| `model_final.pkl` | Modèle Random Forest entraîné |
| `label_encoders.pkl` | Encodeurs des variables catégoriques |
| `profils_utilisateurs.pkl` | 8 410 profils comportementaux |

## Installation

```bash
pip install -r requirements.txt
```

## Base de données PostgreSQL

Créer une base nommée `agent_ia` (PostgreSQL local, port 5432). Les tables `transactions` et `cartes_bloquees` sont créées automatiquement au premier démarrage de l'API (`init_db()` dans `api.py`).

Configuration de connexion à adapter dans `api.py` :

```python
DB_CONFIG = {
    'host':     'localhost',
    'port':     5432,
    'dbname':   'agent_ia',
    'user':     'postgres',
    'password': 'votre_mot_de_passe'
}
```

## Configuration de l'envoi d'email (OTP)

`actions.py` utilise Gmail SMTP. Il faut un mot de passe d'application Google (et non le mot de passe principal du compte) à configurer dans le fichier.

## Lancer l'API

```bash
uvicorn api:app --reload --port 8000
```

Documentation interactive Swagger : `http://localhost:8000/docs`

Identifiants par défaut : `admin` / `agent2026` (codés en dur — voir perspectives d'amélioration dans le rapport).

## Lancer le dashboard

```bash
streamlit run dashboard.py
```

## Lancer la boucle continue de l'agent

```bash
python agent.py
```

Commandes interactives dans le terminal :
- `s` + Entrée → injecter une transaction suspecte
- `q` + Entrée → quitter

## Lancer les tests

```bash
python tests.py
```

Résultats sauvegardés dans `rapport_tests.json`.
