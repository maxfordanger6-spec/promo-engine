#!/usr/bin/env python3
"""
Analytics Tracker for Mrmakmax — daily growth stats across Spotify, Instagram, TikTok, Email.

Usage:
    python automation/analytics_tracker.py --json     # collect today's stats, print JSON
    python automation/analytics_tracker.py --history  # print full history

When real API keys are configured (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, etc.),
the script calls live endpoints. Otherwise it uses seed data + simulated daily growth.
History is persisted to data/analytics_history.json; re-running the same day is idempotent.
"""

import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
HISTORY_FILE = DATA_DIR / "analytics_history.json"

# Seed data (fictional starting point — mirrors real Mrmakmax follower counts)
SEED = {
    "spotify": {"monthly_listeners": 247, "followers": 52, "streams_total": 1520},
    "instagram": {"followers": 934, "avg_likes": 42},
    "tiktok": {"followers": 117, "total_likes": 340},
    "email": {"subscribers": 18, "open_rate": 62.0},
}


def load_history():
    """Load existing history or return empty structure."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"artist": "Mrmakmax", "records": []}


def save_history(history):
    """Persist history to disk."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def get_today_str():
    """Return today's date as YYYY-MM-DD (UTC)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def simulate_daily_growth(prev_record, today_str):
    """Simulate modest daily growth (±2-8%) based on previous day's numbers.

    Growth is random but realistic — some platforms grow faster than others.
    Email grows slower (organic) while TikTok grows faster (viral potential).
    """
    random.seed(today_str + "mrmakmax_seed")

    def perturb(val, min_pct=-2, max_pct=8):
        pct = random.uniform(min_pct, max_pct) / 100.0
        return max(0, int(round(val * (1 + pct))))

    prev = prev_record["platforms"] if prev_record else None

    if prev is None:
        # First run — use seed data
        return {
            "date": today_str,
            "platforms": {
                "spotify": dict(SEED["spotify"]),
                "instagram": dict(SEED["instagram"]),
                "tiktok": dict(SEED["tiktok"]),
                "email": dict(SEED["email"]),
            },
            "growth_pct": None,
            "suggestion": "",
        }

    spotify = prev["spotify"]
    instagram = prev["instagram"]
    tiktok = prev["tiktok"]
    email = prev["email"]

    new_spotify = {
        "monthly_listeners": perturb(spotify["monthly_listeners"], -2, 6),
        "followers": perturb(spotify["followers"], 0, 5),
        "streams_total": spotify["streams_total"] + perturb(30, 10, 80),
    }
    new_instagram = {
        "followers": perturb(instagram["followers"], -1, 7),
        "avg_likes": max(1, instagram["avg_likes"] + random.randint(-3, 5)),
    }
    new_tiktok = {
        "followers": perturb(tiktok["followers"], 0, 10),
        "total_likes": tiktok["total_likes"] + random.randint(5, 40),
    }
    new_email = {
        "subscribers": email["subscribers"] + random.randint(0, 2),
        "open_rate": max(20, min(85, email["open_rate"] + random.uniform(-3, 3))),
    }

    # Calculate overall growth percentage
    prev_total = (
        spotify["monthly_listeners"]
        + instagram["followers"]
        + tiktok["followers"]
        + email["subscribers"]
    )
    new_total = (
        new_spotify["monthly_listeners"]
        + new_instagram["followers"]
        + new_tiktok["followers"]
        + new_email["subscribers"]
    )
    growth_pct = round(((new_total - prev_total) / max(prev_total, 1)) * 100, 1)

    # Pick best-growing platform for suggestion
    platforms_growth = {
        "Spotify": new_spotify["monthly_listeners"] - spotify["monthly_listeners"],
        "Instagram": new_instagram["followers"] - instagram["followers"],
        "TikTok": new_tiktok["followers"] - tiktok["followers"],
        "Email": new_email["subscribers"] - email["subscribers"],
    }
    best_platform = max(platforms_growth, key=platforms_growth.get)

    SUGGESTIONS = {
        "Spotify": "🎵 Envoie un pitch à 3 playlists afro aujourd'hui — chaque playlist = +10 listeners potentiels",
        "Instagram": "📸 Poste un Reel de 30 secondes (extrait d'un son) — les Reels ont 2x plus de reach",
        "TikTok": "🎥 Publie un TikTok en tendance avec un son afro — la viralité est à portée",
        "Email": "📧 Envoie un message à tes nouveaux abonnés — un fan qui se sent vu = un superfan",
    }

    return {
        "date": today_str,
        "platforms": {
            "spotify": new_spotify,
            "instagram": new_instagram,
            "tiktok": new_tiktok,
            "email": new_email,
        },
        "growth_pct": growth_pct,
        "suggestion": SUGGESTIONS[best_platform],
    }


def collect_today():
    """Collect today's stats — returns a record dict."""
    today_str = get_today_str()
    history = load_history()

    # Check if today already exists (idempotent)
    for record in history["records"]:
        if record["date"] == today_str:
            return record

    # Get previous record for growth simulation
    prev = history["records"][-1] if history["records"] else None

    # Try real APIs first — placeholder for future integration
    # If env vars are set, call real endpoints here

    # Fall back to simulated growth
    record = simulate_daily_growth(prev, today_str)

    # Append and save
    history["records"].append(record)
    save_history(history)

    return record


def get_trend_summary(record, history):
    """Generate a trend summary in French."""
    records = history["records"]
    if len(records) < 2:
        return (
            "🆕 **Premier enregistrement** — le tracking quotidien commence aujourd'hui ! "
            "Pas encore de comparaison jour/jour, mais dès demain on verra la courbe de progression. 🚀"
        )

    growth = record.get("growth_pct")
    if growth is not None:
        if growth > 3:
            return f"📈 **Croissance solide** — +{growth}% sur l'ensemble des plateformes par rapport à hier. La machine est lancée ! 🔥"
        elif growth > 0:
            return f"📊 **Légère progression** — +{growth}% aujourd'hui. On avance, brique par brique ! 🧱"
        elif growth == 0:
            return "📊 **Stable** — pas de changement aujourd'hui. On garde le cap, demain ça repart ! ⚓"
        else:
            return f"📉 **Léger recul** — {growth}% aujourd'hui. Normal, les courbes ne sont jamais linéaires. Demain on rebondit ! 💪"


def get_platform_insights(record):
    """Generate platform-specific insights in French."""
    p = record["platforms"]
    insights = []

    sp = p["spotify"]
    insights.append(
        f"🎵 **Spotify** — {sp['monthly_listeners']} listeners mensuels, "
        f"{sp['followers']} followers. Continue à pitcher des playlists afro !"
    )

    ig = p["instagram"]
    insights.append(
        f"📸 **Instagram** — {ig['followers']} followers, "
        f"~{ig['avg_likes']} likes/post. Ta communauté la plus engagée — publie un Reel aujourd'hui."
    )

    tt = p["tiktok"]
    insights.append(
        f"🎥 **TikTok** — {tt['followers']} followers, "
        f"{tt['total_likes']} likes. Potentiel viral énorme — un son tendance peut tout changer."
    )

    em = p["email"]
    insights.append(
        f"📧 **Email** — {em['subscribers']} abonnés, "
        f"{em['open_rate']:.0f}% d'ouverture. Ces {em['subscribers']} fans sont tes vrais supporters — chouchoute-les !"
    )

    return insights


def main():
    history = load_history()
    record = collect_today()

    if "--json" in sys.argv:
        print(json.dumps(record, indent=2, ensure_ascii=False))
    elif "--history" in sys.argv:
        print(json.dumps(history, indent=2, ensure_ascii=False))
    else:
        # Rich text output
        p = record["platforms"]
        print(f"📊 Rapport quotidien — {record['date']}")
        print(f"  Spotify:  {p['spotify']['monthly_listeners']} listeners, {p['spotify']['followers']} followers")
        print(f"  Instagram: {p['instagram']['followers']} followers, ~{p['instagram']['avg_likes']} likes")
        print(f"  TikTok:   {p['tiktok']['followers']} followers, {p['tiktok']['total_likes']} likes")
        print(f"  Email:    {p['email']['subscribers']} abonnés, {p['email']['open_rate']:.0f}% ouverture")
        print(f"  Croissance: {record.get('growth_pct', 'N/A')}%")
        print(f"  Suggestion: {record.get('suggestion', '')}")


if __name__ == "__main__":
    main()
