"""
Analytics Tracker — Collects and stores growth metrics for Mrmakmax.
Pulls data from public APIs and stores in MongoDB.
"""
import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analytics-tracker")


async def fetch_spotify_stats(artist_id: str = None) -> dict:
    """
    Fetch Spotify stats.
    Note: Requires Spotify API credentials for real data.
    For now, returns placeholder — to be configured with real API keys.
    """
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not spotify_client_id or not spotify_client_secret:
        logger.info("Spotify API not configured — using mock data")
        return {
            "monthly_listeners": 0,
            "followers": 0,
            "popularity": 0,
            "_note": "Configure SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET for real data",
        }

    import httpx

    try:
        # Get access token
        async with httpx.AsyncClient() as client:
            auth_resp = await client.post(
                "https://accounts.spotify.com/api/token",
                data={"grant_type": "client_credentials"},
                auth=(spotify_client_id, spotify_client_secret),
                timeout=15,
            )
            token = auth_resp.json().get("access_token")

            # Fetch artist
            artist_id = artist_id or os.getenv("SPOTIFY_ARTIST_ID", "")
            if not artist_id:
                return {"error": "No Spotify artist ID configured"}

            artist_resp = await client.get(
                f"https://api.spotify.com/v1/artists/{artist_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=15,
            )
            data = artist_resp.json()

            return {
                "monthly_listeners": data.get("followers", {}).get("total", 0),
                "followers": data.get("followers", {}).get("total", 0),
                "popularity": data.get("popularity", 0),
                "genres": data.get("genres", []),
            }
    except Exception as e:
        logger.error(f"Spotify fetch failed: {e}")
        return {"error": str(e)}


async def fetch_social_stats() -> dict:
    """
    Fetch social media follower counts.
    Note: Most platforms require API keys. This provides the structure.
    """
    stats = {}

    # Instagram — would need Facebook Graph API
    stats["instagram_followers"] = 0

    # TikTok — would need TikTok API
    stats["tiktok_followers"] = 0

    # YouTube — would need YouTube Data API
    stats["youtube_subscribers"] = 0

    # Twitter/X — would need Twitter API
    stats["twitter_followers"] = 0

    return stats


async def collect_all_stats(artist_id: str = None) -> dict:
    """
    Collect all available stats.
    """
    spotify = await fetch_spotify_stats(artist_id)
    social = await fetch_social_stats()

    return {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "timestamp": datetime.utcnow().isoformat(),
        "spotify_monthly_listeners": spotify.get("monthly_listeners", 0),
        "spotify_followers": spotify.get("followers", 0),
        "spotify_popularity": spotify.get("popularity", 0),
        **social,
    }


async def save_to_mongodb(stats: dict):
    """Save stats to MongoDB via the Promo Engine API."""
    api_url = os.getenv("PROMO_API_URL", "http://localhost:8080")
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{api_url}/api/analytics",
                json=stats,
                timeout=15,
            )
            if resp.status_code == 200:
                logger.info(f"Stats saved: {stats.get('date')}")
            else:
                logger.error(f"Failed to save stats: {resp.status_code}")
    except Exception as e:
        logger.error(f"Cannot reach API: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analytics Tracker")
    parser.add_argument("--artist-id", help="Spotify artist ID")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    async def main():
        stats = await collect_all_stats(args.artist_id)
        if args.json:
            print(json.dumps(stats, indent=2, default=str))
        else:
            print(f"📊 {stats['date']}:")
            print(f"  Spotify: {stats['spotify_monthly_listeners']:,} monthly listeners")
            print(f"  Instagram: {stats['instagram_followers']:,} followers")
            print(f"  TikTok: {stats['tiktok_followers']:,} followers")
            print(f"  YouTube: {stats['youtube_subscribers']:,} subscribers")

        # Try to save to MongoDB
        await save_to_mongodb(stats)

    asyncio.run(main())
