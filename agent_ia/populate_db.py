import requests
import pandas as pd
import time
from datetime import datetime

API_URL = "http://localhost:8000"

# Authentification
r = requests.post(f"{API_URL}/login", json={"username": "admin", "password": "agent2026"})
TOKEN = r.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Charger le dataset
print("Chargement du dataset...")
df_tx = pd.read_csv(r'C:\Users\Pc\Desktop\TER\ieee-fraud-detection\train_transaction.csv')
df_id = pd.read_csv(r'C:\Users\Pc\Desktop\TER\ieee-fraud-detection\train_identity.csv')
df = df_tx.merge(df_id, on='TransactionID', how='left')
df = df[df['DeviceType'].notna()].copy()

COLONNES = ['TransactionAmt', 'card1', 'DeviceType', 'DeviceInfo', 'id_30', 'id_31', 'TransactionDT']
df = df[COLONNES].dropna().copy()

# Piocher 400 transactions aléatoires
sample = df.sample(400, random_state=42)

LOCATIONS = [
    "Paris, France", "Lyon, France", "Marseille, France",
    "Londres, Royaume-Uni", "Berlin, Allemagne", "Madrid, Espagne",
    "Moscou, Russie", "Beijing, Chine", "Lagos, Nigeria",
    "New York, USA", "Dubai, UAE"
]

print(f"Insertion de {len(sample)} transactions...")
print("-" * 50)

succes = 0
erreurs = 0

for i, (_, row) in enumerate(sample.iterrows()):
    # Débloquer la carte si bloquée
    requests.post(f"{API_URL}/unblock/{int(row['card1'])}", headers=HEADERS)

    # Assigner une localisation — suspecte pour 10% des transactions
    if i % 10 == 0:
        location = LOCATIONS[7 + (i % 3)]  # Moscou, Beijing ou Lagos
    else:
        location = LOCATIONS[i % 6]  # villes françaises/européennes

    tx = {
        "card1": int(row['card1']),
        "DeviceType": str(row['DeviceType']),
        "DeviceInfo": str(row['DeviceInfo']),
        "id_30": str(row['id_30']),
        "id_31": str(row['id_31']),
        "TransactionAmt": float(row['TransactionAmt']),
        "TransactionDT": int(row['TransactionDT']),
        "location": location
    }

    try:
        r = requests.post(f"{API_URL}/analyze", json=tx, headers=HEADERS)
        result = r.json()
        niveau = result.get("niveau", "?")
        emoji = {"VERT": "🟢", "ORANGE": "🟠", "ROUGE": "🔴"}.get(niveau, "⚪")
        print(f"  [{i+1:3d}/400] card1={tx['card1']:5d} | {niveau} {emoji} | score={result.get('score_final', '?')} | {location}")
        succes += 1
    except Exception as e:
        print(f"  [{i+1:3d}/400] Erreur : {e}")
        erreurs += 1

    # Petite pause pour ne pas surcharger l'API
    time.sleep(0.1)

print("-" * 50)
print(f"✅ Terminé — {succes} insertions réussies, {erreurs} erreurs")