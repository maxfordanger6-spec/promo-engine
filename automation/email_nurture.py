"""
Email Nurture — Automated email sequences to convert visitors into loyal fans.
Templates for welcome, release alerts, newsletters, and re-engagement.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("email-nurture")

# Default sender config
SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
}

ARTIST_NAME = "Mrmakmax"
ARTIST_GENRE = "Afro Pop"
ARTIST_CREW = "nonamesbeats"
LANDING_URL = os.getenv("LANDING_URL", "https://promo-engine-production-74d9.up.railway.app")


# === Email Templates ===

WELCOME_SEQUENCE = [
    {
        "delay_days": 0,
        "subject": "🔥 Bienvenue dans la famille Mrmakmax !",
        "body": f"""
Salut !

Bienvenue dans la famille. Ça veut dire beaucoup pour moi que tu sois là.

Je suis {ARTIST_NAME}, artiste {ARTIST_GENRE} et co-fondateur de {ARTIST_CREW}. 
Ma mission : faire danser le monde avec des sons qui viennent du cœur.

🎵 **Par où commencer ?**
→ Écoute mon dernier son ici : {LANDING_URL}
→ Suis-moi sur Instagram @nonamesbeats pour les coulisses
→ Réponds à cet email et dis-moi d'où tu viens !

Je te préviens : y'aura des exclus, des surprises, et beaucoup de musique.

Avec love,
{ARTIST_NAME} 💜
"""
    },
    {
        "delay_days": 3,
        "subject": "🎵 Tu veux savoir comment je crée mes sons ?",
        "body": f"""
Hey !

3 jours que t'es dans la famille. J'espère que t'as kiffé le premier son.

Aujourd'hui je veux te partager un peu de mon process créatif :

🎹 **Mes inspirations du moment :**
• Les vibrations afro pop de Burna Boy et Rema
• Les mélodies soul de Tems
• Les prods hybrides de Pheelz et Sarz

💡 **Fun fact :** La plupart de mes mélodies viennent quand je suis sous la douche ou à 3h du mat. La créativité, ça se contrôle pas !

🎧 **Ce que je prépare :** Un nouveau projet qui fusionne afro pop et R&B. T'auras les exclus en premier.

Dis-moi : c'est quoi TON son afro préféré en ce moment ? Réponds à cet email, je lis tout.

Stay vibing,
{ARTIST_NAME} 🎵
"""
    },
    {
        "delay_days": 7,
        "subject": "🎁 Une exclu pour toi (vraie exclu)",
        "body": f"""
Fam !

Une semaine déjà. Pour te remercier d'être là, voici une exclu :

🎬 **Un extrait INÉDIT de mon prochain son**
→ {LANDING_URL}

Personne d'autre ne l'a entendu. Juste la famille.

📲 **Ce que j'aimerais que tu fasses (si t'as aimé) :**
1. Dis-moi ce que t'en penses en répondant à cet email
2. Partage le lien de ma page avec UN•E ami•e qui kiffe l'afro
3. Suis-moi sur les réseaux pour les prochaines exclus

C'est grâce à des vrais fans comme toi que la musique vit.

100% love,
{ARTIST_NAME} 🔥
"""
    },
]

RELEASE_ALERT = {
    "subject": "🚨 DROP ALERT : Nouveau son dispo MAINTENANT",
    "body": f"""
FAMILLE !!!

Le jour est arrivé. Mon nouveau son est DISPONIBLE PARTOUT.

🎵 **Écoute maintenant :** {LANDING_URL}

C'est un morceau spécial. Il parle de [thème]. Je l'ai écrit pendant [contexte]. 
J'espère qu'il va te toucher comme il m'a touché.

**3 choses que tu peux faire pour m'aider (gratuitement) :**

1. 📱 **Stream** le son sur ta plateforme préférée
2. 🔄 **Partage** sur tes stories avec la mention @nonamesbeats
3. 💬 **Commente** "🔥" sur mon dernier post Instagram

Chaque stream, chaque partage, chaque commentaire — ça compte ÉNORMÉMENT pour un artiste indé comme moi.

Merci d'être là. Sans toi, la musique n'existe pas.

Let's gooo,
{ARTIST_NAME} 🚀
"""
}

NEWSLETTER_TEMPLATE = {
    "subject": "📰 Mrmakmax Monthly — Ce qui s'est passé ce mois",
    "body": f"""
Salut la famille !

Voici les vibes du mois :

---

🎵 **NOUVEAU SON**
[Détails du dernier drop]

📈 **STATS DU MOIS**
• {{{{spotify_listeners}}}} nouveaux listeners sur Spotify
• {{{{new_fans}}}} nouveaux fans dans la famille email
• Top pays : {{{{top_countries}}}}

🎤 **À VENIR**
[Prochains drops, events, collabs]

🎧 **MA PLAYLIST DU MOIS**
Les sons qui m'ont inspiré ces 30 derniers jours :
1. [Son 1]
2. [Son 2]
3. [Son 3]

💜 **SHOUTOUT**
Merci à [fan du mois] pour le soutien !

---

Reste connecté. Le meilleur est à venir.

{ARTIST_NAME}
"""
}

REENGAGEMENT_TEMPLATE = {
    "subject": "Tu nous manques 💜",
    "body": f"""
Hey !

Ça fait un moment qu'on s'est pas parlé. Pas de stress, la vie c'est busy.

Juste pour te dire : t'es toujours dans la famille, et voici ce que t'as manqué :

🎵 [Dernier son sorti]
🎬 [Dernier clip]
🎤 [Prochain event]

Si t'es plus intéressé•e, tu peux te désabonner en bas. Zéro rancune.

Mais si t'es toujours là... réponds juste "🔥" et je saurai que t'es vivant•e 😄

Love,
{ARTIST_NAME}
"""
}


def get_sequence(sequence_name: str = "welcome") -> list:
    """Get a complete email sequence."""
    sequences = {
        "welcome": WELCOME_SEQUENCE,
        "release": [RELEASE_ALERT],
        "newsletter": [NEWSLETTER_TEMPLATE],
        "reengagement": [REENGAGEMENT_TEMPLATE],
    }
    return sequences.get(sequence_name, WELCOME_SEQUENCE)


def generate_email_report() -> dict:
    """Generate a report of email nurture status and next actions."""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "active_sequences": {
            "welcome": "3 emails sur 7 jours — automatique à l'inscription",
            "release": "1 email immédiat — déclenché manuellement à chaque drop",
            "newsletter": "1 email par mois — récap mensuel",
            "reengagement": "1 email après 30 jours d'inactivité",
        },
        "recommended_actions": [
            "Configurer SMTP_USERNAME et SMTP_PASSWORD pour l'envoi automatique",
            "Connecter un service comme SendGrid ou Brevo pour de meilleurs taux de délivrabilité",
            "Ajouter Google Analytics UTM tags aux liens pour tracker les clics",
            "Tester la welcome sequence avec ton propre email d'abord",
        ],
        "best_practices": [
            "📧 Taux d'ouverture cible : 20-30% (moyenne musique : 18%)",
            "🕐 Meilleur moment d'envoi : mardi ou jeudi, 10h-11h",
            "📱 60% des emails sont lus sur mobile — garde le format court",
            "🎯 Segmenter les fans par pays pour des messages plus pertinents",
        ],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Email Nurture System")
    parser.add_argument("--mode", choices=["sequence", "preview", "report", "all"], default="report")
    parser.add_argument("--type", default="welcome", choices=["welcome", "release", "newsletter", "reengagement"])
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.mode == "sequence":
        seq = get_sequence(args.type)
        print(f"📧 {args.type.upper()} sequence ({len(seq)} emails):")
        for i, email in enumerate(seq):
            print(f"  Day {email.get('delay_days', 0)}: {email['subject']}")
    elif args.mode == "preview":
        seq = get_sequence(args.type)
        email = seq[0]
        print(f"Subject: {email['subject']}")
        print(f"Body preview: {email['body'][:300]}...")
    elif args.mode in ("report", "all"):
        report = generate_email_report()
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(f"📊 Email Nurture Report — {report['date']}")
            print("\n📁 Active Sequences:")
            for name, desc in report["active_sequences"].items():
                print(f"  {name}: {desc}")
            print("\n💡 Recommended Actions:")
            for action in report["recommended_actions"]:
                print(f"  • {action}")
