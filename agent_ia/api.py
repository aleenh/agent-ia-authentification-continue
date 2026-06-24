from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import psycopg2
import psycopg2.extras
import jwt
import random
import string

from scoring import score_combine, decision_agent, profils

from actions import generer_otp, envoyer_otp_email
otp_pending = {}

# ─── CONFIG ───────────────────────────────────────────────
SECRET_KEY = "agent_ia_secret_2026"
ALGORITHM  = "HS256"
TOKEN_EXPIRE_MINUTES = 60

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "agent_ia",
    "user": "postgres",
    "password": "root"
}

app = FastAPI(title="Agent IA — Authentification Continue", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ─── CONNEXION PostgreSQL ─────────────────────────────────
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# ─── INITIALISATION DES TABLES ────────────────────────────
def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP,
            card1 INTEGER,
            score_ml REAL,
            score_comp REAL,
            score_final REAL,
            niveau VARCHAR(10),
            action TEXT,
            device VARCHAR(50),
            montant REAL,
            location VARCHAR(100)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cartes_bloquees (
            card1 INTEGER PRIMARY KEY,
            timestamp TIMESTAMP,
            raison TEXT,
            nouveau_code VARCHAR(20)
        )
    ''')
    conn.commit()
    c.close()
    conn.close()

init_db()

# ─── MODÈLES Pydantic ─────────────────────────────────────
class Transaction(BaseModel):
    card1: int
    DeviceType: str
    DeviceInfo: str
    id_30: str
    id_31: str
    TransactionAmt: float
    TransactionDT: int
    location: Optional[str] = "Paris, France"

class LoginRequest(BaseModel):
    username: str
    password: str

# ─── JWT ──────────────────────────────────────────────────
def creer_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verifier_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

# ─── ENDPOINTS ────────────────────────────────────────────

@app.post("/login")
def login(req: LoginRequest):
    if req.username == "admin" and req.password == "agent2026":
        return {"access_token": creer_token(req.username), "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Identifiants incorrects")


@app.post("/analyze")
def analyze(tx: Transaction, user: str = Depends(verifier_token)):
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Vérifier si la carte est bloquée
    c.execute("SELECT * FROM cartes_bloquees WHERE card1 = %s", (tx.card1,))
    bloquee = c.fetchone()

    if bloquee:
        c.close()
        conn.close()
        return {
            "card1": tx.card1,
            "niveau": "ROUGE",
            "action": "Carte bloquée — déblocage requis",
            "score_final": 0.0,
            "bloquee": True
        }

    # Calcul du score
    tx_dict = tx.dict()
    s_final, s_ml, s_comp = score_combine(tx_dict)
    niveau, action, emoji = decision_agent(s_final)

    # Sauvegarder la transaction
    c.execute('''
        INSERT INTO transactions
        (timestamp, card1, score_ml, score_comp, score_final, niveau, action, device, montant, location, id_30, id_31)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        datetime.now(), int(tx.card1), float(s_ml), float(s_comp),
        float(s_final), niveau, action, tx.DeviceType, float(tx.TransactionAmt), 
        tx.location, tx.id_30, tx.id_31
    ))

    # Bloquer la carte si ROUGE
    if niveau == "ROUGE":
        nouveau_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        c.execute('''
            INSERT INTO cartes_bloquees (card1, timestamp, raison, nouveau_code)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (card1) DO UPDATE
            SET timestamp = EXCLUDED.timestamp,
                raison = EXCLUDED.raison,
                nouveau_code = EXCLUDED.nouveau_code
        ''', (tx.card1, datetime.now(), "Score de risque critique", nouveau_code))

    conn.commit()
    c.close()
    conn.close()

    return {
        "card1": tx.card1,
        "score_ml": s_ml,
        "score_comp": s_comp,
        "score_final": s_final,
        "niveau": niveau,
        "action": action,
        "emoji": emoji,
        "location": tx.location,
        "bloquee": niveau == "ROUGE"
    }


@app.get("/status")
def get_status(user: str = Depends(verifier_token)):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM transactions")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM transactions WHERE niveau = 'ROUGE'")
    rouges = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM transactions WHERE niveau = 'ORANGE'")
    oranges = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM cartes_bloquees")
    bloquees = c.fetchone()[0]
    c.close()
    conn.close()

    return {
        "total_transactions": total,
        "alertes_rouge": rouges,
        "alertes_orange": oranges,
        "cartes_bloquees": bloquees,
        "statut_agent": "actif"
    }


@app.get("/transactions")
def get_transactions(limit: int = 20, user: str = Depends(verifier_token)):
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute('''
        SELECT timestamp, card1, score_final, niveau, action, device, montant, location
        FROM transactions ORDER BY id DESC LIMIT %s
    ''', (limit,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/unblock/{card1}")
def unblock(card1: int, user: str = Depends(verifier_token)):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM cartes_bloquees WHERE card1 = %s", (card1,))
    affected = c.rowcount
    conn.commit()
    c.close()
    conn.close()

    if affected == 0:
        raise HTTPException(status_code=404, detail="Carte non trouvée dans les cartes bloquées")

    return {"message": f"Carte {card1} débloquée avec succès", "card1": card1}


@app.post("/simulate_attack")
def simulate_attack(user: str = Depends(verifier_token)):
    carte = int(profils[profils['nb_transactions'] >= 5]['card1'].iloc[0])
    profil = profils[profils['card1'] == carte].iloc[0]

    tx = Transaction(
        card1 = carte,
        DeviceType = 'mobile' if profil['appareil_habituel'] == 'desktop' else 'desktop',
        DeviceInfo = 'unknown_device',
        id_30 = 'Android 9.0',
        id_31 = 'unknown_browser',
        TransactionAmt = float(profil['montant_moyen'] * 15),
        TransactionDT = 3 * 3600,
        location = "Moscou, Russie"
    )
    return analyze(tx, user)


@app.get("/cartes_bloquees")
def get_cartes_bloquees(user: str = Depends(verifier_token)):
    conn = get_conn()
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    c.execute("SELECT card1, timestamp, raison FROM cartes_bloquees")
    rows = c.fetchall()
    c.close()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/send_otp")
def send_otp(data: dict, user: str = Depends(verifier_token)):
    card1 = data.get("card1")
    otp = generer_otp()
    otp_pending[card1] = {
        "code": otp,
        "expire_at": datetime.now().timestamp() + 90  # 90 secondes
    }
    envoyer_otp_email(otp, card1)
    return {"message": "OTP envoyé par email", "expire_in": 90}


@app.post("/verify_otp")
def verify_otp(data: dict, user: str = Depends(verifier_token)):
    card1 = data.get("card1")
    code_saisi = data.get("code")

    if card1 not in otp_pending:
        raise HTTPException(status_code=400, detail="Aucun OTP en attente pour cette carte")

    info = otp_pending[card1]
    if datetime.now().timestamp() > info["expire_at"]:
        del otp_pending[card1]
        raise HTTPException(status_code=400, detail="Code expiré")

    if code_saisi != info["code"]:
        raise HTTPException(status_code=400, detail="Code incorrect")

    del otp_pending[card1]
    return {"valide": True, "message": "Identité confirmée"}