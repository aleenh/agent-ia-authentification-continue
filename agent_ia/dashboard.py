import streamlit as st
import requests
import time
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────
API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="Agent IA — Authentification Continue",
    page_icon="🔐",
    layout="wide"
)

# ─── AUTHENTIFICATION ─────────────────────────────────────
def get_token():
    if 'token' not in st.session_state:
        r = requests.post(f"{API_URL}/login", json={"username": "admin", "password": "agent2026"})
        st.session_state.token = r.json()["access_token"]
    return st.session_state.token

def headers():
    return {"Authorization": f"Bearer {get_token()}"}

# ─── FONCTIONS API ────────────────────────────────────────
def get_status():
    try:
        r = requests.get(f"{API_URL}/status", headers=headers())
        return r.json()
    except:
        return None

def get_transactions(limit=20):
    try:
        r = requests.get(f"{API_URL}/transactions?limit={limit}", headers=headers())
        return r.json()
    except:
        return []

def get_cartes_bloquees():
    try:
        r = requests.get(f"{API_URL}/cartes_bloquees", headers=headers())
        return r.json()
    except:
        return []

def simulate_attack():
    try:
        r = requests.post(f"{API_URL}/simulate_attack", headers=headers())
        return r.json()
    except:
        return None

def unblock_card(card1):
    try:
        r = requests.post(f"{API_URL}/unblock/{card1}", headers=headers())
        return r.json()
    except:
        return None

# ─── COULEUR NIVEAU ───────────────────────────────────────
def couleur_niveau(niveau):
    if niveau == "VERT":
        return "🟢"
    elif niveau == "ORANGE":
        return "🟠"
    else:
        return "🔴"

def badge_niveau(niveau):
    colors = {"VERT": "#1D9E75", "ORANGE": "#E07B00", "ROUGE": "#C0392B"}
    color = colors.get(niveau, "#888")
    return f'<span style="background:{color};color:white;padding:3px 10px;border-radius:12px;font-weight:bold;font-size:13px">{niveau}</span>'

# ─── INTERFACE ────────────────────────────────────────────
st.title("🔐 Agent IA — Authentification Continue et Adaptive")
st.markdown("---")

# Récupérer les données
status = get_status()
transactions = get_transactions(20)
cartes_bloquees = get_cartes_bloquees()

# ─── MÉTRIQUES PRINCIPALES ────────────────────────────────
if status:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total transactions", status["total_transactions"])
    col2.metric("🔴 Alertes ROUGE", status["alertes_rouge"])
    col3.metric("🟠 Alertes ORANGE", status["alertes_orange"])
    col4.metric("🚫 Cartes bloquées", status["cartes_bloquees"])

st.markdown("---")

# ─── DEUX COLONNES PRINCIPALES ────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📋 Historique des transactions")

    if transactions:
        # Dernière transaction
        last = transactions[0]
        niveau = last.get("niveau", "")
        score  = last.get("score_final", 0)

        st.markdown(f"**Dernière transaction** — Carte `{last['card1']}` | "
                    f"Score : `{score}` | {badge_niveau(niveau)} | "
                    f"📍 {last.get('location', 'N/A')}",
                    unsafe_allow_html=True)

        # Jauge de risque
        st.markdown("**Niveau de confiance :**")
        couleur_barre = "#1D9E75" if score >= 0.8 else "#E07B00" if score >= 0.5 else "#C0392B"
        st.markdown(f"""
        <div style="background:#eee;border-radius:10px;height:20px;width:100%">
            <div style="background:{couleur_barre};width:{int(score*100)}%;height:20px;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;color:white;font-size:12px">
                {int(score*100)}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        # Tableau historique
        st.markdown("**Toutes les transactions :**")
        for tx in transactions:
            emoji = couleur_niveau(tx.get("niveau", ""))
            st.markdown(
                f"{emoji} `{tx['timestamp'][:19]}` — Carte **{tx['card1']}** | "
                f"Score : `{tx['score_final']}` | {tx.get('device','N/A')} | "
                f"**{tx['montant']}$** | 📍{tx.get('location','N/A')}",
                unsafe_allow_html=True
            )
    else:
        st.info("Aucune transaction enregistrée pour l'instant.")

with col_right:
    st.subheader("🎮 Simulation")

    # Bouton simulation attaque
    if st.button("🚨 Simuler une attaque", use_container_width=True, type="primary"):
        result = simulate_attack()
        if result:
            niveau = result.get("niveau", "")
            st.markdown(f"**Résultat :** {badge_niveau(niveau)}", unsafe_allow_html=True)
            st.markdown(f"- Carte : `{result['card1']}`")
            if result.get("bloquee") and result.get("score_final", 0) == 0.0:
                st.error("🚫 Cette carte est déjà bloquée — débloquez-la d'abord !")
            else:
                st.markdown(f"- Score ML : `{result.get('score_ml', 'N/A')}`")
                st.markdown(f"- Score Comportemental : `{result.get('score_comp', 'N/A')}`")
                st.markdown(f"- Score Final : `{result.get('score_final', 'N/A')}`")
                st.markdown(f"- Localisation : 📍 {result.get('location', 'N/A')}")
                if result.get("bloquee"):
                    st.error("🚫 Carte automatiquement bloquée !")

    # Cartes bloquées
    st.subheader("🚫 Cartes bloquées")
    if cartes_bloquees:
        for carte in cartes_bloquees:
            st.markdown(f"🔴 Carte **{carte['card1']}**")
            st.markdown(f"  Bloquée le : `{str(carte['timestamp'])[:19]}`")
            st.markdown(f"  Raison : {carte['raison']}")
            if st.button(f"✅ Débloquer {carte['card1']}", key=f"unblock_{carte['card1']}"):
                result = unblock_card(carte['card1'])
                if result:
                    st.success(f"Carte {carte['card1']} débloquée !")
                    time.sleep(1)
                    st.rerun()
    else:
        st.success("Aucune carte bloquée ✅")

    st.markdown("---")

    # Statut agent
    st.subheader("⚙️ Statut de l'agent")
    st.markdown(f"🟢 **Agent : actif**")
    st.markdown(f"🔄 Refresh automatique toutes les 10 secondes")

# ─── AUTO-REFRESH ─────────────────────────────────────────
st.markdown("---")
st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")
time.sleep(10)
st.rerun()