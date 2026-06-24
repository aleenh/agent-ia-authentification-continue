import pickle
import numpy as np

# Chargement des artefacts
with open('model_final.pkl', 'rb') as f:
    modele = pickle.load(f)

with open('label_encoders.pkl', 'rb') as f:
    label_encoders = pickle.load(f)

with open('profils_utilisateurs.pkl', 'rb') as f:
    profils = pickle.load(f)


def calculer_score(transaction, profil):
    scores = {}

    scores['appareil'] = 1.0 if transaction['DeviceType'] == profil['appareil_habituel'] else 0.0
    scores['os'] = 1.0 if transaction['id_30'] == profil['os_habituel'] else 0.0

    z_montant = abs(transaction['TransactionAmt'] - profil['montant_moyen']) / (profil['montant_std'] + 1)
    scores['montant'] = max(0.0, 1.0 - z_montant / 3)

    heure = (transaction['TransactionDT'] // 3600) % 24
    z_heure = abs(heure - profil['heure_moyenne']) / (profil['heure_std'] + 1)
    scores['heure'] = max(0.0, 1.0 - z_heure / 3)

    score_global = (
        0.30 * scores['appareil'] +
        0.25 * scores['os']      +
        0.25 * scores['montant'] +
        0.20 * scores['heure']
    )
    return round(score_global, 4), scores


def score_combine(transaction_row, poids_ml=0.6, poids_scoring=0.4):
    # Encodage des colonnes catégoriques
    cat_cols = ['DeviceType', 'DeviceInfo', 'id_30', 'id_31']
    cat_encoded = []
    for col in cat_cols:
        le  = label_encoders[col]
        val = transaction_row.get(col, 'inconnu')
        encoded = le.transform([val])[0] if val in le.classes_ else -1
        cat_encoded.append(encoded)

    # Vecteur d'entrée dans le même ordre qu'à l'entraînement
    import pandas as pd
    X_input = pd.DataFrame([[
        transaction_row['TransactionAmt'],
        transaction_row['card1'],
        cat_encoded[0],
        cat_encoded[1],
        cat_encoded[2],
        cat_encoded[3],
    ]], columns=['TransactionAmt', 'card1', 'DeviceType', 'DeviceInfo', 'id_30', 'id_31'])

    # Score ML
    proba_fraude = modele.predict_proba(X_input)[0][1]
    score_ml = 1 - proba_fraude

    # Score comportemental
    card1_val = transaction_row['card1']
    profil_carte = profils[profils['card1'] == card1_val]
    score_comp = calculer_score(transaction_row, profil_carte.iloc[0])[0] if len(profil_carte) > 0 else 0.5

    score_final = poids_ml * score_ml + poids_scoring * score_comp
    return round(score_final, 4), round(score_ml, 4), round(score_comp, 4)


def decision_agent(score):
    if score >= 0.8:
        return 'VERT', 'Accès accordé — session normale', '✅'
    elif score >= 0.6:
        return 'ORANGE', 'Vérification requise — code OTP envoyé', '⚠️'
    else:
        return 'ROUGE', 'Accès bloqué — alerte générée, nouveau code requis', '🚨'