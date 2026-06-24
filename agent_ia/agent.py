import time
import random
import pandas as pd
import pickle
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from scoring import score_combine, decision_agent, profils
from actions import action_orange, action_rouge

# Charger le dataset pour piocher des transactions réelles
print("Chargement du dataset...")
df_complet = pd.read_csv(r'C:\Users\Pc\Desktop\TER\ieee-fraud-detection\train_transaction.csv')
identity   = pd.read_csv(r'C:\Users\Pc\Desktop\TER\ieee-fraud-detection\train_identity.csv')
df_complet = df_complet.merge(identity, on='TransactionID', how='left')
df_complet = df_complet[df_complet['DeviceType'].notna()].copy()

COLONNES = ['TransactionAmt', 'card1', 'DeviceType', 'DeviceInfo', 'id_30', 'id_31', 'TransactionDT']

# Transaction suspecte pour injection manuelle
TRANSACTION_SUSPECTE = None  # sera définie via inject_suspicious()


def get_random_transaction():
    """Pioche une transaction aléatoire dans le dataset."""
    row = df_complet[COLONNES].sample(1).iloc[0]
    return row.to_dict()


def inject_suspicious():
    """Injecte une transaction suspecte au prochain cycle."""
    global TRANSACTION_SUSPECTE
    carte = profils[profils['nb_transactions'] >= 5]['card1'].iloc[0]
    profil = profils[profils['card1'] == carte].iloc[0]
    TRANSACTION_SUSPECTE = {
        'card1':          carte,
        'DeviceType':     'mobile' if profil['appareil_habituel'] == 'desktop' else 'desktop',
        'DeviceInfo':     'unknown_device',
        'id_30':          'Android 9.0',
        'id_31':          'unknown_browser',
        'TransactionAmt': profil['montant_moyen'] * 15,
        'TransactionDT':  3 * 3600
    }
    print("\n⚠️  Transaction suspecte injectée — sera analysée au prochain cycle.\n")


def analyser_transaction(transaction):
    s_final, s_ml, s_comp = score_combine(transaction)
    niveau, action, emoji = decision_agent(s_final)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
          f"card1={transaction['card1']} | "
          f"ML={s_ml} | Comp={s_comp} | Final={s_final} "
          f"→ {niveau} {emoji}")

    if niveau == 'ORANGE':
        action_orange(transaction['card1'])
    elif niveau == 'ROUGE':
        action_rouge(transaction['card1'])
    else:
        print(f"  Action : {action}")

    # Log général
    with open('agent_log.txt', 'a') as f:
        f.write(f"{datetime.now()} | card1={transaction['card1']} | "
                f"score={s_final} | niveau={niveau}\n")


def cycle_agent():
    """Un cycle de l'agent — appelé toutes les 30 secondes."""
    global TRANSACTION_SUSPECTE

    if TRANSACTION_SUSPECTE is not None:
        print("\n🔴 INJECTION SUSPECTE DÉTECTÉE")
        analyser_transaction(TRANSACTION_SUSPECTE)
        TRANSACTION_SUSPECTE = None
    else:
        transaction = get_random_transaction()
        analyser_transaction(transaction)


# Démarrage de l'agent
if __name__ == '__main__':
    print("=" * 60)
    print("  Agent IA — Authentification Continue et Adaptive")
    print("  Cycle : toutes les 30 secondes")
    print("  Commandes : [s] injecter transaction suspecte | [q] quitter")
    print("=" * 60)

    scheduler = BackgroundScheduler()
    scheduler.add_job(cycle_agent, 'interval', seconds=30)
    scheduler.start()

    # Premier cycle immédiat
    cycle_agent()

    try:
        while True:
            cmd = input()
            if cmd.strip().lower() == 's':
                inject_suspicious()
            elif cmd.strip().lower() == 'q':
                print("Arrêt de l'agent.")
                scheduler.shutdown()
                break
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Agent arrêté.")