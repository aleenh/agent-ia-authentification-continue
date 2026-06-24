import smtplib
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ⚠️ Remplace par tes infos
EMAIL_EXPEDITEUR = "aleenhoblos@gmail.com"
MOT_DE_PASSE_APP = "zcmp njli arsv qqpo"  # mot de passe d'application Gmail
EMAIL_DESTINATAIRE = "aleenhoblos@gmail.com"  # pour la démo, tu t'envoies à toi-même

OTP_EXPIRATION = 120  # secondes


def generer_otp():
    """Génère un code OTP à 6 chiffres."""
    return ''.join(random.choices(string.digits, k=6))


def envoyer_otp_email(otp, card1):
    """Envoie le code OTP par email via Gmail SMTP."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_EXPEDITEUR
    msg['To'] = EMAIL_DESTINATAIRE
    msg['Subject'] = "🔐 Code de vérification — Agent IA"

    corps = f"""
Bonjour,

Une activité inhabituelle a été détectée sur votre compte.

Carte : {card1}
Code OTP : {otp}
Expire dans : {OTP_EXPIRATION} secondes

Si vous êtes à l'origine de cette connexion, saisissez ce code pour confirmer votre identité.
Dans le cas contraire, ignorez ce message — votre accès sera automatiquement bloqué.

— Agent IA d'Authentification Continue
    """

    msg.attach(MIMEText(corps, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as serveur:
            serveur.login(EMAIL_EXPEDITEUR, MOT_DE_PASSE_APP)
            serveur.sendmail(EMAIL_EXPEDITEUR, EMAIL_DESTINATAIRE, msg.as_string())
        print(f"  📧 Email OTP envoyé à {EMAIL_DESTINATAIRE}")
        return True
    except Exception as e:
        print(f"  ❌ Erreur envoi email : {e}")
        print(f"  🔁 Fallback terminal — Code OTP : {otp}")
        return False


def verifier_otp(otp):
    """Demande à l'utilisateur de saisir le code OTP dans le terminal."""
    debut = time.time()
    print(f"  ⏳ Vous avez {OTP_EXPIRATION} secondes pour saisir le code OTP.")

    tentative = input("  Entrez le code OTP : ").strip()
    elapsed = time.time() - debut

    if elapsed > OTP_EXPIRATION:
        print("  ⌛ Code expiré — accès bloqué.")
        return False
    elif tentative == otp:
        print("  ✅ Code correct — accès accordé.")
        return True
    else:
        print("  ❌ Code incorrect — accès bloqué.")
        return False


def action_orange(card1):
    """Niveau ORANGE : envoyer OTP et vérifier."""
    print(f"  ⚠️  Vérification requise pour la carte {card1}")
    otp = generer_otp()
    envoyer_otp_email(otp, card1)
    return verifier_otp(otp)


def action_rouge(card1):
    """Niveau ROUGE : bloquer et générer un nouveau code d'accès."""
    nouveau_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    print(f"  🚨 Accès bloqué pour la carte {card1}")
    print(f"  🔑 Nouveau code d'accès généré : {nouveau_code}")
    print(f"  📧 (En production : envoyé par email à l'utilisateur)")

    # Log de sécurité
    with open('security_log.txt', 'a') as f:
        from datetime import datetime
        f.write(f"{datetime.now()} | BLOCAGE | card1={card1} | nouveau_code={nouveau_code}\n")

    return False