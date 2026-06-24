import requests
import time
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

API_URL = "http://localhost:8000"

DB_CONFIG = {
    "host": "localhost", "port": 5432,
    "dbname": "agent_ia", "user": "postgres", "password": "root"
}

# ─── AUTHENTIFICATION ─────────────────────────────────────
def get_token():
    r = requests.post(f"{API_URL}/login", json={"username": "admin", "password": "agent2026"})
    return r.json()["access_token"]

TOKEN = get_token()
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# ─── RÉCUPÉRER LES DONNÉES DEPUIS POSTGRESQL ──────────────
def get_transactions_from_db():
    conn = psycopg2.connect(**DB_CONFIG)
    c = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Transactions VERT — considérées comme normales
    c.execute("""
        SELECT * FROM transactions 
        WHERE niveau = 'VERT' 
        ORDER BY RANDOM() LIMIT 20
    """)
    normales = c.fetchall()
    
    # Transactions ROUGE — considérées comme suspectes
    c.execute("""
        SELECT * FROM transactions 
        WHERE niveau = 'ROUGE' 
        ORDER BY RANDOM() LIMIT 20
    """)
    suspectes = c.fetchall()
    
    c.close()
    conn.close()
    return normales, suspectes

# ─── TEST SUR VRAIES DONNÉES ──────────────────────────────
def tester_transaction_db(tx, niveau_attendu):
    """Rejoue une transaction depuis la DB avec les vraies valeurs."""
    requests.post(f"{API_URL}/unblock/{tx['card1']}", headers=HEADERS)
    
    payload = {
        "card1": tx['card1'],
        "DeviceType": tx['device'] if tx['device'] else 'desktop',
        "DeviceInfo": tx['device'] if tx['device'] else 'desktop',
        "id_30": tx['id_30'] if tx['id_30'] else 'Windows 10',
        "id_31": tx['id_31'] if tx['id_31'] else 'chrome 63',
        "TransactionAmt": tx['montant'],
        "TransactionDT":  43200,
        "location": tx['location'] if tx['location'] else "Paris, France"
    }
    
    debut = time.time()
    r = requests.post(f"{API_URL}/analyze", json=payload, headers=HEADERS)
    temps_reponse = (time.time() - debut) * 1000
    
    result = r.json()
    niveau_obtenu = result.get("niveau", "INCONNU")
    correct = niveau_obtenu == niveau_attendu
    
    return {
        "card1": tx['card1'],
        "montant": tx['montant'],
        "niveau_attendu": niveau_attendu,
        "niveau_obtenu": niveau_obtenu,
        "score_final": result.get("score_final", 0),
        "correct": correct,
        "temps_ms": round(temps_reponse, 2)
    }

# ─── EXÉCUTION ────────────────────────────────────────────
print("=" * 65)
print(" TESTS SUR VRAIES DONNÉES — Agent IA")
print(f" {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print("=" * 65)

normales, suspectes = get_transactions_from_db()
print(f"\n Transactions normales récupérées  : {len(normales)}")
print(f" Transactions suspectes récupérées : {len(suspectes)}")

resultats = []

print("\n--- TRANSACTIONS NORMALES (attendu : VERT) ---")
for i, tx in enumerate(normales):
    r = tester_transaction_db(tx, "VERT")
    resultats.append(r)
    statut = "✅" if r["correct"] else "❌"
    print(f" [{i+1:2d}] card1={r['card1']:5d} | {r['montant']:8.1f}$ | Score={r['score_final']} → {r['niveau_obtenu']} {statut}")

print("\n--- TRANSACTIONS SUSPECTES (attendu : ROUGE) ---")
for i, tx in enumerate(suspectes):
    r = tester_transaction_db(tx, "ROUGE")
    resultats.append(r)
    statut = "✅" if r["correct"] else "❌"
    print(f" [{i+1:2d}] card1={r['card1']:5d} | {r['montant']:8.1f}$ | Score={r['score_final']} → {r['niveau_obtenu']} {statut}")

# ─── MÉTRIQUES ────────────────────────────────────────────
print("\n" + "=" * 65)
print(" MÉTRIQUES FINALES")
print("=" * 65)

tests_suspects = [r for r in resultats if r["niveau_attendu"] == "ROUGE"]
faux_acceptes = [r for r in tests_suspects if r["niveau_obtenu"] == "VERT"]
FAR = len(faux_acceptes) / len(tests_suspects) * 100 if tests_suspects else 0

tests_normaux = [r for r in resultats if r["niveau_attendu"] == "VERT"]
faux_rejetes = [r for r in tests_normaux if r["niveau_obtenu"] == "ROUGE"]
FRR = len(faux_rejetes) / len(tests_normaux) * 100 if tests_normaux else 0

corrects = [r for r in resultats if r["correct"]]
precision = len(corrects) / len(resultats) * 100
temps_moyen = sum(r["temps_ms"] for r in resultats) / len(resultats)
temps_max = max(r["temps_ms"] for r in resultats)
temps_min = min(r["temps_ms"] for r in resultats)

print(f"\n  Transactions testées : {len(resultats)}")
print(f" FAR (taux fausse acceptation) : {FAR:.1f}%")
print(f" FRR (taux faux rejet) : {FRR:.1f}%")
print(f" EER (point d'égalité FAR=FRR) : {(FAR+FRR)/2:.1f}%")
print(f" Précision globale : {precision:.1f}%")
print(f"\n Temps de réponse moyen : {temps_moyen:.1f} ms")
print(f" Temps de réponse minimum : {temps_min:.1f} ms")
print(f" Temps de réponse maximum : {temps_max:.1f} ms")
print("\n" + "=" * 65)

# Sauvegarde
rapport = {
    "date": datetime.now().isoformat(),
    "nb_transactions": len(resultats),
    "FAR": FAR, "FRR": FRR, "EER": (FAR+FRR)/2,
    "precision": precision,
    "temps_moyen_ms": temps_moyen,
    "temps_max_ms": temps_max,
    "temps_min_ms": temps_min,
    "resultats": resultats
}
with open("rapport_tests.json", "w") as f:
    json.dump(rapport, f, indent=2)

print(" Résultats sauvegardés dans rapport_tests.json")
print("=" * 65)