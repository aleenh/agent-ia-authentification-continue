# Meridian Banque — Démo Agent IA

Interface bancaire React connectée à ta vraie API FastAPI (`api.py`), pour la démo de soutenance.

## Installation

```bash
npm install
```

## Lancer le projet

**1. Lance d'abord ton API FastAPI** (dans ton dossier `agent_ia/`) :
```bash
uvicorn api:app --reload --port 8000
```

**2. Lance ensuite l'appli React** (dans ce dossier) :
```bash
npm run dev
```

Ouvre **http://localhost:5173**

## Identifiants de connexion

- Username : `admin`
- Password : `agent2026`

(Ce sont les identifiants codés en dur dans `api.py`)

## Scénarios de démo

Une fois connecté, 3 boutons permettent de tester les 3 niveaux de l'agent :

1. **Achat habituel** → envoie une transaction normale (desktop, Paris, 45€) → l'API doit retourner VERT
2. **Nouvel appareil** → envoie une transaction avec un iPhone non reconnu (Lyon, 120€) → l'API doit retourner ORANGE → popup OTP
3. **Vol de session** → envoie une transaction suspecte (Moscou, appareil inconnu, 1950€) → l'API doit retourner ROUGE → écran de blocage

## Carte utilisée pour la démo

`card1 = 1009` — choisie car elle a un profil comportemental bien établi dans `profils_utilisateurs.pkl` (appareil habituel : desktop, montant moyen : ~130€).

Si tu veux changer de carte pour la démo, modifie `USER_PROFILE.card1` dans `src/App.jsx`.

## Important avant la démo

- Pense à débloquer la carte 1009 si elle est déjà bloquée depuis un test précédent (`POST /unblock/1009` dans Swagger, ou le bouton "Vérifier mon identité" dans l'appli après un blocage).
- Le scénario ORANGE envoie maintenant un **vrai email** via `/send_otp` (Gmail SMTP configuré dans `actions.py`) et vérifie le code saisi via `/verify_otp`. Le timer est de **90 secondes** pour laisser le temps de recevoir l'email.
- Assure-toi d'avoir bien ajouté les endpoints `/send_otp` et `/verify_otp` dans `api.py` avant de tester ce scénario (voir échange avec Claude pour le code exact).
- Si l'email met du temps à arriver, le bouton reste actif tout le temps du timer (90s) — pense à checker tes spams si rien n'arrive après 20-30s.
