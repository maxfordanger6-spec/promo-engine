"""
Hashtag Optimizer — Research and optimize hashtags for maximum reach on each platform.
Tracks trending hashtags in afro pop / afrobeats niche.
"""
import os
import json
import logging
from datetime import datetime
from collections import OrderedDict

logger = logging.getLogger("hashtag-optimizer")

# Pre-researched hashtag sets by platform and category
HASHTAG_DB = {
    "afro_pop_core": [
        ("#AfroPop", 85), ("#Afrobeats", 95), ("#AfricanMusic", 70),
        ("#AfroFusion", 60), ("#AfroVibes", 75), ("#AfroSound", 55),
        ("#AfroWave", 45), ("#AfroRnB", 50),
    ],
    "afro_pop_french": [
        ("#MusiqueAfro", 40), ("#AfroFrancais", 35), ("#AfroFrance", 30),
        ("#SonAfro", 25), ("#AfroParadis", 20),
    ],
    "discovery": [
        ("#NewMusic", 80), ("#MusicDiscovery", 65), ("#IndieArtist", 55),
        ("#UpcomingArtist", 50), ("#UnsignedArtist", 40), ("#NewArtist", 60),
        ("#MusicPromo", 45), ("#NowPlaying", 70),
    ],
    "instagram": [
        ("#InstaMusic", 60), ("#MusicLover", 50), ("#ExplorePage", 40),
        ("#Reels", 90), ("#Viral", 85), ("#Trending", 75),
        ("#InstaGood", 50), ("#Photooftheday", 45),
    ],
    "tiktok": [
        ("#FYP", 100), ("#Viral", 95), ("#MusicTok", 85),
        ("#AfrobeatTok", 60), ("#NewSound", 55), ("#TrendingSound", 50),
        ("#ForYou", 90), ("#TikTokMusic", 70),
    ],
    "twitter": [
        ("#NowPlaying", 60), ("#MusicTwitter", 55), ("#AfroTwitter", 45),
        ("#NewMusicFriday", 50), ("#np", 40),
    ],
    "youtube": [
        ("#MusicVideo", 70), ("#OfficialAudio", 55), ("#Subscribe", 50),
        ("#AfroMusic", 60), ("#NewVideo", 45),
    ],
}

HASHTAG_STRATEGIES = {
    "instagram": {
        "total": 25,
        "mix": {
            "core_niche": 8,   # Afro pop / afrobeats
            "discovery": 6,    # New music / indie
            "platform": 6,     # Insta-specific
            "custom_branded": 3,  # #Mrmakmax #nonamesbeats etc
            "location": 2,     # #Paris #France etc
        },
        "placement": "Dans les commentaires (pas la caption)",
    },
    "tiktok": {
        "total": 5,
        "mix": {
            "core_niche": 2,
            "discovery": 1,
            "platform": 2,
            "custom_branded": 0,
        },
        "placement": "Dans la caption (max 5 hashtags)",
    },
    "twitter": {
        "total": 3,
        "mix": {
            "core_niche": 1,
            "discovery": 1,
            "platform": 1,
            "custom_branded": 0,
        },
        "placement": "Dans le tweet (max 3 hashtags)",
    },
    "youtube": {
        "total": 15,
        "mix": {
            "core_niche": 5,
            "discovery": 4,
            "platform": 4,
            "custom_branded": 2,
        },
        "placement": "Dans la description",
    },
}

CUSTOM_BRANDED = ["#Mrmakmax", "#nonamesbeats", "#LeSplash", "#MrmakmaxMusic"]

LOCATION_HASHTAGS = {
    "paris": ["#ParisMusic", "#ParisAfro", "#Paris"],
    "france": ["#FrenchMusic", "#MusiqueFrancaise", "#FranceArtist"],
    "africa": ["#AfricaMusic", "#AfricanArtist", "#MadeInAfrica"],
    "global": ["#WorldMusic", "#GlobalSound", "#InternationalArtist"],
}


def get_hashtags_for_platform(platform: str = "instagram", category: str = "all", count: int = 15) -> list:
    """Get optimized hashtags for a specific platform."""
    strategy = HASHTAG_STRATEGIES.get(platform, HASHTAG_STRATEGIES["instagram"])
    
    selected = []
    
    if category in ("all", "core"):
        tags = sorted(HASHTAG_DB["afro_pop_core"], key=lambda x: x[1], reverse=True)
        selected.extend([t[0] for t in tags[:strategy["mix"]["core_niche"]]])
    
    if category in ("all", "discovery"):
        tags = sorted(HASHTAG_DB["discovery"], key=lambda x: x[1], reverse=True)
        selected.extend([t[0] for t in tags[:strategy["mix"]["discovery"]]])
    
    if category in ("all", "platform"):
        platform_tags = HASHTAG_DB.get(platform, [])
        tags = sorted(platform_tags, key=lambda x: x[1], reverse=True)
        selected.extend([t[0] for t in tags[:strategy["mix"]["platform"]]])
    
    if category in ("all", "branded"):
        selected.extend(CUSTOM_BRANDED[:strategy["mix"].get("custom_branded", 2)])
    
    # Shuffle to avoid always the same order
    import random
    random.shuffle(selected)
    
    return selected[:count]


def generate_hashtag_set(platform: str = "instagram", content_type: str = "new_release",
                          mood: str = "hype", location: str = "global") -> dict:
    """
    Generate a complete optimized hashtag set for a post.
    """
    strategy = HASHTAG_STRATEGIES.get(platform, HASHTAG_STRATEGIES["instagram"])
    tags = get_hashtags_for_platform(platform, "all", strategy["total"])
    
    # Add location-specific tags
    loc_tags = LOCATION_HASHTAGS.get(location, LOCATION_HASHTAGS["global"])
    import random
    random.shuffle(tags)
    
    # Add content-specific bonus tags
    bonus = {
        "new_release": ["#OutNow", "#NewDrop", "#FreshMusic"],
        "bts": ["#BehindTheScenes", "#StudioVibes", "#CreativeProcess"],
        "lyric": ["#Lyrics", "#MusicLyrics", "#Songwriting"],
        "performance": ["#LiveMusic", "#Performance", "#StageVibes"],
    }
    content_bonus = bonus.get(content_type, [])
    
    final_tags = tags + content_bonus[:2]
    
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "platform": platform,
        "content_type": content_type,
        "strategy": f"{strategy['total']} hashtags — {strategy['placement']}",
        "hashtags": final_tags[:strategy["total"]],
        "hashtag_string": " ".join(final_tags[:strategy["total"]]),
        "custom_branded": CUSTOM_BRANDED,
        "best_practices": [
            f"📱 {platform.title()}: {strategy['placement']}",
            "🔄 Alterne les hashtags entre chaque post (pas la même liste à chaque fois)",
            "📊 Teste différents sets et garde ceux qui performent le mieux",
            "🚫 Évite les hashtags bannis/shadowbanned (ex: #follow4follow, #like4like)",
            "🎯 Utilise des hashtags de taille moyenne (10K-500K posts) — plus de chances d'être vu",
        ],
    }


def get_trending_in_niche() -> list:
    """Return currently trending hashtags in the afro pop niche."""
    # In a real implementation, this would fetch from APIs
    return [
        {"tag": "#AfrobeatsToTheWorld", "momentum": "rising", "reason": "Trending après les Grammy"},
        {"tag": "#AfroPop2026", "momentum": "stable", "reason": "Hashtag annuel"},
        {"tag": "#NewAfricanSound", "momentum": "rising", "reason": "Mouvement émergent"},
        {"tag": "#AltéVibes", "momentum": "rising", "reason": "Scène alté en croissance"},
    ]


def analyze_hashtag_performance(platform: str = "instagram") -> dict:
    """Placeholder for hashtag analytics."""
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "platform": platform,
        "recommendation": {
            "best_size": "10K-500K posts",
            "best_count": HASHTAG_STRATEGIES[platform]["total"],
            "why": "Les hashtags de taille moyenne donnent plus de visibilité que les #FYP (trop saturés)",
        },
        "top_performing_categories": ["afro_pop_core", "discovery"],
        "avoid": ["#follow4follow", "#like4like", "#followtrain", "#music", "#love"],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Hashtag Optimizer")
    parser.add_argument("--mode", choices=["set", "list", "trending", "analyze", "all"], default="set")
    parser.add_argument("--platform", default="instagram", choices=["instagram", "tiktok", "twitter", "youtube"])
    parser.add_argument("--type", default="new_release", choices=["new_release", "bts", "lyric", "performance", "general"])
    parser.add_argument("--mood", default="hype")
    parser.add_argument("--location", default="global")
    parser.add_argument("--count", type=int, default=15)
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.mode == "list":
        tags = get_hashtags_for_platform(args.platform, "all", args.count)
        print(" ".join(tags))
    elif args.mode == "trending":
        trending = get_trending_in_niche()
        for t in trending:
            print(f"{t['tag']} — {t['momentum']} ({t['reason']})")
    elif args.mode == "analyze":
        result = analyze_hashtag_performance(args.platform)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"📊 Hashtag Analysis — {args.platform}")
            print(f"  Best size: {result['recommendation']['best_size']}")
            print(f"  Best count: {result['recommendation']['best_count']}")
            print(f"  Avoid: {', '.join(result['avoid'])}")
    elif args.mode in ("set", "all"):
        result = generate_hashtag_set(args.platform, args.type, args.mood, args.location)
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"🏷️ HASHTAG SET — {result['platform']} ({result['content_type']})")
            print(f"\n{result['hashtag_string']}")
            print(f"\n📌 Strategy: {result['strategy']}")
