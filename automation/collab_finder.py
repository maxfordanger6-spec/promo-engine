"""
Collab Finder — Discover similar artists for features, cross-promotion, and networking.
Find producers, vocalists, and beatmakers in the afro pop niche.
"""
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("collab-finder")

# Artist database for afro pop / afrobeats collaborations
COLLAB_TARGETS = {
    "producers": [
        {"name": "Pheelz", "genre": "afro pop producer", "style": "melodic afro", "location": "Nigeria", "notable": "Produced for BNXN, Olamide", "collab_type": "beat + prod"},
        {"name": "Sarz", "genre": "afro pop producer", "style": "afro fusion", "location": "Nigeria", "notable": "Produced for Wizkid, Skepta", "collab_type": "beat + prod"},
        {"name": "Tempoe", "genre": "afro producer", "style": "afro pop / amapiano", "location": "Nigeria", "notable": "Produced 'Soweto'", "collab_type": "beat"},
        {"name": "Kel-P", "genre": "afro producer", "style": "afro pop / R&B", "location": "Nigeria", "notable": "Produced for Burna Boy", "collab_type": "prod"},
        {"name": "Shizzi", "genre": "afro producer", "style": "afro pop", "location": "Nigeria", "notable": "Produced for Davido", "collab_type": "beat + prod"},
    ],
    "vocalists": [
        {"name": "Ruger", "genre": "afro pop", "style": "dancehall afro", "location": "Nigeria", "notable": "Hit 'Asiwaju'", "collab_type": "featuring"},
        {"name": "BNXN", "genre": "afro fusion", "style": "melodic afro", "location": "Nigeria", "notable": "Grammy nominee", "collab_type": "featuring"},
        {"name": "Joeboy", "genre": "afro pop", "style": "romantic afro", "location": "Nigeria", "notable": "Hit 'Baby'", "collab_type": "featuring"},
        {"name": "Victony", "genre": "afro pop", "style": "alté / trap afro", "location": "Nigeria", "notable": "Unique voice", "collab_type": "featuring"},
        {"name": "Ayra Starr", "genre": "afro pop", "style": "afro pop / R&B", "location": "Nigeria", "notable": "Mavin Records", "collab_type": "featuring (female)"},
        {"name": "Tems", "genre": "alté", "style": "alté / soul", "location": "Nigeria", "notable": "Grammy winner", "collab_type": "featuring (female)"},
        {"name": "Oxlade", "genre": "afro pop", "style": "melodic afro", "location": "Nigeria", "notable": "Hit 'Kulosa'", "collab_type": "featuring"},
        {"name": "Omah Lay", "genre": "afro fusion", "style": "afro soul", "location": "Nigeria", "notable": "Unique sound", "collab_type": "featuring"},
    ],
    "beatmakers": [
        {"name": "Niphkeys", "genre": "afro pop beats", "style": "afro pop / street", "location": "Nigeria", "notable": "Produced for Zinoleesky", "collab_type": "beat lease"},
        {"name": "RewardBeatz", "genre": "afro producer", "style": "afro pop", "location": "Nigeria", "notable": "YouTube beatmaker", "collab_type": "beat lease"},
        {"name": "BlaiseBeatz", "genre": "afro producer", "style": "afro pop / amapiano", "location": "Nigeria", "notable": "Hot producer", "collab_type": "beat lease"},
    ],
    "rappers": [
        {"name": "Odumodublvck", "genre": "afro drill / rap", "style": "drill afro", "location": "Nigeria", "notable": "Rising star", "collab_type": "featuring rap"},
        {"name": "PsychoYP", "genre": "afro rap", "style": "trap / afro", "location": "Nigeria", "notable": "Apex Village", "collab_type": "featuring rap"},
    ],
}

COLLAB_TIPS = [
    "🤝 Commence par interagir avec leur contenu avant de proposer une collab",
    "📧 DM poli et court : qui tu es, pourquoi tu penses que ça matcherait",
    "🎵 Propose un son déjà enregistré (pas juste une idée vague)",
    "💰 Pour les producteurs établis : prépare un budget (50-200€)",
    "🆓 Pour les beatmakers YouTube : beaucoup proposent des leases à 20-50€",
    "📱 Le networking sur Twitter/X fonctionne mieux que les DM froids",
    "🎤 Offre de faire le featuring gratuitement si l'autre artiste est plus gros que toi",
    "🔄 Propose un échange : je chante sur ton son si tu chantes sur le mien",
]


def find_collaborators(category: str = "all", level: str = "all") -> list:
    """Find potential collaborators by category."""
    if category == "all":
        results = []
        for cat, artists in COLLAB_TARGETS.items():
            for artist in artists:
                artist["category"] = cat
                results.append(artist)
        return results
    return COLLAB_TARGETS.get(category, [])


def generate_collab_strategy() -> dict:
    """Generate a complete collaboration strategy."""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "strategy": "Construire un réseau dans l'afro pop — qualité > quantité",
        "phases": [
            {
                "phase": 1,
                "name": "Beatmakers (budget 20-100€)",
                "action": "Achète 2-3 beats qualité pro sur YouTube/BeatStars",
                "targets": find_collaborators("beatmakers", "all"),
                "why": "Un bon beat, c'est 50% du son. Investis dans la qualité.",
            },
            {
                "phase": 2,
                "name": "Producers indépendants (budget 50-200€)",
                "action": "Contacte des producteurs émergents pour une session",
                "targets": find_collaborators("producers", "all")[:3],
                "why": "Un producer peut élever ton son au niveau supérieur.",
            },
            {
                "phase": 3,
                "name": "Artistes émergents (cross-promo gratuite)",
                "action": "Trouve 2-3 artistes à ton niveau pour un feat mutuel",
                "targets": find_collaborators("vocalists", "all")[:5],
                "why": "Cross-promo = vous doublez vos audiences respectives.",
            },
            {
                "phase": 4,
                "name": "Artistes établis (relations long terme)",
                "action": "Networking, engagement, patience — pas de DM direct pour l'instant",
                "targets": find_collaborators("vocalists", "all")[5:],
                "why": "Construis ta réputation d'abord. Les gros feats viennent naturellement.",
            },
        ],
        "dm_template": """
Salut [NOM] ! Je suis Mrmakmax, artiste afro pop.

Je suis ton travail depuis un moment, surtout [SON/ALBUM]. 
J'adore comment tu [QUALITÉ SPÉCIFIQUE].

Je prépare un projet et je pense que nos styles pourraient vraiment bien marcher ensemble.

Si t'es open, je peux t'envoyer une démo. Pas de pression !

Keep killing it 🔥
""",
        "budget_estimate": {
            "phase_1_beats": "40-200€ (2-3 beats)",
            "phase_2_producer": "100-300€ (1 session)",
            "phase_3_collab": "0€ (cross-promo mutuelle)",
            "total": "140-500€ pour un projet complet",
        },
    }


def suggest_daily_networking() -> dict:
    """Daily networking actions for organic relationship building."""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "daily_actions": [
            "📱 Commente 3 posts d'artistes dans ta niche (authentique, pas 'fire 🔥')",
            "🎵 Écoute et partage 1 nouveau son afro pop en story",
            "💬 Réponds aux DM et commentaires sur TES posts",
            "🔍 Découvre 2 nouveaux artistes afro pop émergents",
            "📧 Si pertinent : 1 DM poli à un artiste/producer (pas de spam)",
        ],
        "weekly_goals": [
            "1 nouvelle connexion avec un artiste/producer",
            "3 beats sauvegardés pour le prochain projet",
            "1 session studio/bookée",
        ],
        "tips": COLLAB_TIPS[:4],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collab Finder")
    parser.add_argument("--mode", choices=["list", "strategy", "daily", "all"], default="all")
    parser.add_argument("--category", default="all", choices=["all", "producers", "vocalists", "beatmakers", "rappers"])
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.mode == "list":
        artists = find_collaborators(args.category)
        for a in artists:
            print(f"🎤 {a['name']} — {a['genre']} ({a.get('location', '?')})")
            print(f"   💡 {a.get('notable', '')}")
    elif args.mode == "strategy":
        result = generate_collab_strategy()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"🤝 COLLAB STRATEGY — {result['date']}")
            for phase in result["phases"]:
                print(f"\n📍 Phase {phase['phase']}: {phase['name']}")
                print(f"   {phase['action']}")
                print(f"   Budget: {phase['why']}")
    elif args.mode == "daily":
        result = suggest_daily_networking()
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"📅 Daily Networking — {result['date']}")
            for action in result["daily_actions"]:
                print(f"  {action}")
    elif args.mode == "all":
        strategy = generate_collab_strategy()
        daily = suggest_daily_networking()
        print(json.dumps({"strategy": strategy, "daily": daily}, indent=2, ensure_ascii=False))
