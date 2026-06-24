# Agent IA d'Authentification Continue et Adaptive

Projet de TER — Master 1 Informatique, parcours Données et Systèmes Connectés
Université Jean Monnet — Saint-Étienne

**Étudiante :** Hoblos Alinne

---

## Description

Ce projet propose un agent IA capable de surveiller en continu le comportement d'un utilisateur lors de transactions bancaires, et d'adapter automatiquement le niveau de sécurité (VERT / ORANGE / ROUGE) selon le risque détecté, en s'appuyant sur le principe de sécurité Zero Trust.

L'agent combine deux approches complémentaires :
- Un modèle de **machine learning** (Random Forest) entraîné sur le dataset [IEEE CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)
- Un **moteur de scoring comportemental** qui compare chaque transaction au profil habituel de l'utilisateur (8 410 profils construits à partir du dataset)

## Structure du dépôt

```
agent-ia-ter/
├── agent_ia/          → Backend : scoring, agent, API FastAPI, dashboard Streamlit
├── banque-app/         → Frontend : interface bancaire de démonstration (React)
├── notebook/           → Notebook Jupyter d'entraînement du modèle ML
├── rapport/            → Rapport final du TER (PDF)
└── README.md
```

## Démarrage rapide

### 1. Backend (agent_ia/)

```bash
cd agent_ia
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

L'API est accessible sur `http://localhost:8000`, documentation interactive sur `http://localhost:8000/docs`.

Prérequis : PostgreSQL démarré localement (base `agent_ia`, voir `agent_ia/README.md` pour le schéma).

### 2. Dashboard technique (Streamlit)

```bash
cd agent_ia
streamlit run dashboard.py
```

Accessible sur `http://localhost:8501`.

### 3. Interface bancaire de démonstration (React)

```bash
cd banque-app
npm install
npm run dev
```

Accessible sur `http://localhost:5173`. Voir `banque-app/README.md` pour les identifiants de connexion et les scénarios de démo.

> Important : l'API (étape 1) doit toujours être lancée avant le dashboard et l'interface React.

## Architecture

```
Interfaces clientes (Dashboard Streamlit / Interface React)
            │  HTTP REST + JWT
            ▼
       API FastAPI (9 endpoints)
            │
    ┌───────┴────────┐
    ▼                ▼
scoring.py        actions.py
(score ML +    (OTP email, blocage)
 comportemental)
    │
    ▼
agent.py (boucle continue, 30s)
    │
    ▼
PostgreSQL (transactions, cartes_bloquees)
```

## Résultats principaux

| Métrique | Tests contrôlés | Tests sur vraies données |
|----------|------------------|---------------------------|
| FAR | 0% | 10% |
| FRR | 0% | 0% |
| EER | 0% | 5% |
| Précision | 100% | 65% |

Détails complets, justification des choix techniques et discussion critique des résultats : voir le rapport dans `rapport/`.

## Stack technique

- **Machine Learning :** scikit-learn (Random Forest), pandas
- **Backend :** FastAPI, PostgreSQL, PyJWT, APScheduler, smtplib
- **Frontend technique :** Streamlit
- **Frontend démonstration :** React, Tailwind CSS, lucide-react

## Licence

Projet académique réalisé dans le cadre d'un TER de Master 1 — Université Jean Monnet, 2025-2026.
