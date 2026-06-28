"""
Playlist Pitching — Find and contact Spotify playlist curators in the afro pop niche.
Helps generate pitch messages and track submissions.
"""
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger("playlist-pitcher")

# Known afro pop / afrobeats playlists and curators
AFRO_PLAYLISTS = [
    {
        "name": "Afro Pop Hits",
        "curator": "Spotify Editorial",
        "followers": "2M+",
        "genre": "afro pop",
        "submission_type": "spotify_for_artists",
        "link": "https://open.spotify.com/playlist/37i9dQZF1DXc8kgYqQLMfH",
        "difficulty": "hard",
        "tip": "Pitch au moins 2 semaines avant la sortie via Spotify for Artists",
    },
    {
        "name": "African Heat",
        "curator": "Spotify Editorial",
        "followers": "1.5M+",
        "genre": "african music",
        "submission_type": "spotify_for_artists",
        "link": "https://open.spotify.com/playlist/37i9dQZF1DWUI1rlvkdQnP",
        "difficulty": "hard",
        "tip": "Focus sur la qualité de production et l'authenticité du son africain",
    },
    {
        "name": "Afrobeats Hits",
        "curator": "Spotify Editorial",
        "followers": "1M+",
        "genre": "afrobeats",
        "submission_type": "spotify_for_artists",
        "link": "https://open.spotify.com/playlist/37i9dQZF1DX7GqyyDCN1WX",
        "difficulty": "hard",
        "tip": "Tempo élevé, énergie dansante — parfait pour les sons upbeat",
    },
    {
        "name": "Fresh Finds Africa",
        "curator": "Spotify Editorial",
        "followers": "500K+",
        "genre": "african independent",
        "submission_type": "spotify_for_artists",
        "link": "https://open.spotify.com/playlist/37i9dQZF1DWSWNiyXQAvbl",
        "difficulty": "medium",
        "tip": "Playlist pour artistes émergents — MEILLEURE chance pour toi",
    },
    {
        "name": "Naija Party",
        "curator": "Spotify Editorial",
        "followers": "300K+",
        "genre": "naija/afro",
        "submission_type": "spotify_for_artists",
        "link": "https://open.spotify.com/playlist/37i9dQZF1DX7GqyyDCN2qX",
        "difficulty": "medium",
        "tip": "Vibes nigérianes — énergie festive et rythmes dansants",
    },
    {
        "name": "Afro R&B",
        "curator": "Spotify Editorial",
        "followers": "200K+",
        "genre": "afro r&b",
        "submission_type": "spotify_for_artists",
        "link": "https://open.spotify.com/playlist/37i9dQZF1DX1SbnWoT2BmJ",
        "difficulty": "medium",
        "tip": "Pour les sons plus doux, R&B teinté d'afro",
    },
    {
        "name": "Afro Pop FR",
        "curator": "Independent",
        "followers": "50K+",
        "genre": "afro pop france",
        "submission_type": "direct_dm",
        "difficulty": "easy",
        "tip": "Cherche le curateur sur Instagram/Twitter et envoie un DM poli",
    },
    {
        "name": "Afrobeats 2026",
        "curator": "Independent",
        "followers": "30K+",
        "genre": "afrobeats new",
        "submission_type": "submit_hub",
        "difficulty": "easy",
        "tip": "Soumets via SubmitHub ou Groover — coût 2-5€ par soumission",
    },
]

PITCH_TEMPLATES = {
    "hype": """
Hey ! Je m'appelle Mrmakmax, artiste afro pop basé en [ville].

Je te partage mon nouveau son "[TITRE]" — une fusion afro pop/R&B produite par [prod].
Il a déjà généré [X] streams en [Y] jours et les retours sont fous.

🎵 Lien : [URL]

Je pense qu'il pourrait vraiment matcher avec ta playlist [PLAYLIST] parce que [RAISON].

Merci pour ton temps et pour ce que tu fais pour la scène afro ! 🙏
""",
    "personal": """
Salut [CURATOR] !

Je suis Mrmakmax. Je suis ta playlist [PLAYLIST] depuis un moment et j'adore comment tu [COMPLIMENT SPÉCIFIQUE].

Je viens de sortir "[TITRE]" — un son qui, je pense, collerait bien avec l'ambiance que tu proposes.

🎧 Écoute ici : [URL]

Si ça te parle, je serais honoré d'être inclus. Et si c'est pas le bon fit, pas de souci !

Keep doing what you do 🔥
""",
    "short": """
🔥 New drop: "[TITRE]" by Mrmakmax

Afro pop x R&B vibes. Already [X] streams in [Y] days.

Listen: [URL]

Think it'd fit [PLAYLIST] ?

Bless 🙏
""",
}


def get_playlist_targets(genre: str = "afro pop", difficulty: str = "all") -> list:
    """Get curated list of playlists to target."""
    results = AFRO_PLAYLISTS
    if genre and genre != "all":
        results = [p for p in results if genre.lower() in p.get("genre", "").lower()]
    if difficulty and difficulty != "all":
        results = [p for p in results if p.get("difficulty") == difficulty]
    return results


def generate_pitch(song_title: str, playlist_name: str, style: str = "personal", curator_name: str = "") -> str:
    """Generate a playlist pitch message."""
    template = PITCH_TEMPLATES.get(style, PITCH_TEMPLATES["personal"])
    pitch = template.replace("[TITRE]", song_title)
    pitch = pitch.replace("[PLAYLIST]", playlist_name)
    pitch = pitch.replace("[CURATOR]", curator_name or "Curateur")
    pitch = pitch.replace("[URL]", "[LIEN DU SON]")
    return pitch.strip()


def generate_pitch_strategy(song_title: str = "Nouveau Son") -> dict:
    """
    Generate a complete pitching strategy with prioritized targets and pitches.
    """
    easy = get_playlist_targets(difficulty="easy")
    medium = get_playlist_targets(difficulty="medium")
    hard = get_playlist_targets(difficulty="hard")

    strategy = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "song": song_title,
        "phases": [
            {
                "phase": 1,
                "name": "Pré-sortie (2 semaines avant)",
                "action": "Pitcher via Spotify for Artists",
                "targets": hard + medium,
                "pitch": "Pitch éditorial Spotify (300 caractères max) — focus sur l'histoire du son, pas juste le genre",
            },
            {
                "phase": 2,
                "name": "Jour de sortie",
                "action": "DM + SubmitHub",
                "targets": easy,
                "pitch": generate_pitch(song_title, "ta playlist", "short"),
            },
            {
                "phase": 3,
                "name": "Post-sortie (1-2 semaines après)",
                "action": "Follow-up poli + nouvelles playlists",
                "targets": medium,
                "pitch": "Follow-up: 'Hey, je comprends si t'as pas eu le temps. Au cas où, le son est toujours dispo : [URL]. Bonne journée !'",
            },
        ],
        "tips": [
            "🎯 Priorité #1 : Fresh Finds Africa (meilleure chance pour artistes émergents)",
            "📅 Pitch TOUJOURS au moins 2 semaines avant la sortie sur Spotify for Artists",
            "💰 Budget suggéré pour SubmitHub/Groover : 20-30€ par sortie",
            "🤝 Construis des relations avec les curateurs indépendants — DM personnalisé, pas copié-collé",
            "📊 Track tes soumissions dans un spreadsheet : playlist, date, réponse, résultat",
        ],
    }
    return strategy


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Playlist Pitching System")
    parser.add_argument("--mode", choices=["targets", "pitch", "strategy", "all"], default="strategy")
    parser.add_argument("--genre", default="all")
    parser.add_argument("--difficulty", default="all")
    parser.add_argument("--song", default="Nouveau Son")
    parser.add_argument("--style", default="personal", choices=["hype", "personal", "short"])
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.mode == "targets":
        playlists = get_playlist_targets(args.genre, args.difficulty)
        for p in playlists:
            print(f"🎵 {p['name']} — {p['followers']} followers ({p['difficulty']})")
            print(f"   💡 {p['tip']}")
    elif args.mode == "pitch":
        pitch = generate_pitch(args.song, "ta playlist", args.style)
        print(pitch)
    elif args.mode in ("strategy", "all"):
        strategy = generate_pitch_strategy(args.song)
        if args.json:
            print(json.dumps(strategy, indent=2, ensure_ascii=False))
        else:
            print(f"📋 PITCH STRATEGY — {strategy['song']}")
            for phase in strategy["phases"]:
                print(f"\n📍 Phase {phase['phase']}: {phase['name']}")
                print(f"   Action: {phase['action']}")
                print(f"   Playlists: {len(phase['targets'])} cibles")
            print(f"\n💡 Tips:")
            for tip in strategy["tips"]:
                print(f"  {tip}")
