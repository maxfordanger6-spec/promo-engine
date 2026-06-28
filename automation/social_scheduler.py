"""
Social Media Scheduler — Plans and manages promotional posts for Mrmakmax.
Generates captions optimized for each platform with hashtags.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("social-scheduler")

# Afro Pop optimized hashtags
AFRO_POP_HASHTAGS = [
    "#AfroPop", "#Afrobeats", "#AfricanMusic", "#NewMusic",
    "#Mrmakmax", "#nonamesbeats", "#AfroVibes", "#AfroSound",
    "#RnB", "#SoulMusic", "#MusicDiscovery", "#IndieArtist",
    "#UpcomingArtist", "#NewArtist", "#MusicPromo",
]

PLATFORM_HASHTAGS = {
    "instagram": ["#InstaMusic", "#MusicLover", "#Vibes", "#ExplorePage", "#Reels"],
    "tiktok": ["#FYP", "#Viral", "#MusicTok", "#AfrobeatTok", "#NewSound"],
    "twitter": ["#NowPlaying", "#MusicTwitter", "#AfroTwitter", "#NewMusicFriday"],
    "youtube": ["#MusicVideo", "#OfficialAudio", "#Subscribe", "#AfroMusic"],
}


def generate_caption(
    platform: str,
    content_type: str = "general",
    song_title: str = "",
    mood: str = "hype",
) -> str:
    """
    Generate platform-optimized caption with hashtags.
    """
    captions = {
        "new_release": [
            f"🔥 NOUVEAU SON ! '{song_title}' est dispo partout ! Link in bio 🎵",
            f"Le drop est là ! {song_title} — stream maintenant et dis-moi ce que t'en penses 💜",
            f"I've been working on this one... {song_title} OUT NOW on all platforms 🚀",
        ],
        "bts": [
            "Behind the scenes... creating magic in the studio 🎹✨",
            "Late night sessions hit different 🌙 Raw vibes only",
            "This one's special. Can't wait for you to hear it 🎵",
        ],
        "general": [
            "Vibes on vibes 🌊 Afro pop energy all day",
            "Born to make the world dance 💃🕺",
            "Music is the answer. What's the question? 🎵",
        ],
        "engagement": [
            "Quel son tu veux que je drop ensuite ? Dis-moi en commentaire 👇",
            "Tag quelqu'un qui doit entendre ça ⬇️",
            "Quelle est ta chanson préférée du moment ? 🎧",
        ],
    }

    # Pick a random caption from the category
    import random
    category = captions.get(content_type, captions["general"])
    caption = random.choice(category)

    # Platform-specific adjustments
    platform_hashtags = PLATFORM_HASHTAGS.get(platform, [])
    general_hashtags = random.sample(AFRO_POP_HASHTAGS, min(5, len(AFRO_POP_HASHTAGS)))
    all_hashtags = general_hashtags + platform_hashtags[:3]

    # Format
    if platform == "instagram":
        hashtag_str = "\n.\n.\n.\n" + " ".join(all_hashtags)
    elif platform == "tiktok":
        hashtag_str = " ".join(all_hashtags[:5])
    else:
        hashtag_str = " ".join(all_hashtags[:4])

    return f"{caption}\n\n{hashtag_str}"


def create_post_schedule(
    artist: str = "Mrmakmax",
    days: int = 7,
) -> list:
    """
    Create a weekly posting schedule.
    Returns a list of posts with platform, content type, and caption.
    """
    schedule = []

    content_rotation = [
        ("general", None),
        ("new_release", "Latest Drop"),
        ("bts", None),
        ("engagement", None),
        ("general", None),
        ("new_release", "Afro Vibes"),
        ("bts", None),
    ]

    platforms = ["instagram", "tiktok", "twitter"]
    import random

    for day_offset in range(days):
        content_type, song = content_rotation[day_offset % len(content_rotation)]
        platform = platforms[day_offset % len(platforms)]

        post = {
            "day": day_offset + 1,
            "platform": platform,
            "content_type": content_type,
            "caption": generate_caption(
                platform=platform,
                content_type=content_type,
                song_title=song or "",
            ),
            "scheduled_for": f"Day {day_offset + 1}",
        }
        schedule.append(post)

    return schedule


def get_best_posting_times(platform: str = "instagram") -> list:
    """
    Return optimal posting times for each platform (UTC).
    These are general best-practices for music content.
    """
    times = {
        "instagram": ["16:00", "19:00", "12:00"],
        "tiktok": ["15:00", "19:00", "21:00", "10:00"],
        "twitter": ["12:00", "17:00", "20:00"],
        "youtube": ["15:00", "18:00", "11:00"],
    }
    return times.get(platform, ["18:00"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Social Media Scheduler")
    parser.add_argument("--mode", choices=["caption", "schedule", "times"], default="schedule")
    parser.add_argument("--platform", default="instagram")
    parser.add_argument("--type", default="general", help="Content type")
    parser.add_argument("--song", default="", help="Song title")
    parser.add_argument("--days", type=int, default=7)

    args = parser.parse_args()

    if args.mode == "caption":
        caption = generate_caption(platform=args.platform, content_type=args.type, song_title=args.song)
        print(caption)
    elif args.mode == "schedule":
        schedule = create_post_schedule(days=args.days)
        print(json.dumps(schedule, indent=2, ensure_ascii=False))
    elif args.mode == "times":
        times = get_best_posting_times(args.platform)
        print(f"Best times for {args.platform}: {', '.join(times)}")
