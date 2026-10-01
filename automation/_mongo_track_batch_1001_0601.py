"""Track generated content in MongoDB (direct insert — Railway app deleted).
Batch 20261001_060104 (Content Factory cron 2026-10-01 06:01).
"""
import json
import sys
from datetime import datetime

from pymongo import MongoClient

MONGO_URL = "mongodb+srv://hermes.enhh09v.mongodb.net/?appName=promo-engine"
MONGO_USERNAME = "le_splash"
MONGO_PASSWORD = "Mignon12345six"
DB_NAME = "promo_engine"

base = r"C:\Users\nonamesbeats\promo-content"

items = [
    {"type": "fallback_image", "file_path": base + r"\fallback_20261001_060104.png",
     "metadata": {"source": "content_factory_pack", "batch": "20261001_060104"}},
    {"type": "quote_card", "file_path": base + r"\quote_20261001_060104_335.png",
     "metadata": {"quote": "Born to make the world dance", "batch": "20261001_060104"}},
    {"type": "quote_card", "file_path": base + r"\quote_20261001_060104_354.png",
     "metadata": {"quote": "Afro pop is not just music, it's a vibration", "batch": "20261001_060104"}},
    {"type": "promo_banner", "file_path": base + r"\promo_20261001_060104_373.png",
     "metadata": {"title": "NOUVEAU SON DISPONIBLE", "batch": "20261001_060104"}},
]

social_captions = {
    "instagram_quote": "Born to make the world dance 💃🕺\n\n\n.\n.\n.\n#Afrobeats #AfroVibes #NewArtist #NewMusic #AfricanMusic #InstaMusic #MusicLover #Vibes",
    "tiktok_promo": "Vibes on vibes 🌊 Afro pop energy all day\n\n#Afrobeats #IndieArtist #AfroVibes #UpcomingArtist #AfroPop",
    "twitter_quote": "Vibes on vibes 🌊 Afro pop energy all day\n\n#Afrobeats #AfroPop #RnB #AfroSound",
    "facebook_quote": "Born to make the world dance 💃🕺\n\n#IndieArtist #AfroVibes #RnB #nonamesbeats",
    "youtube_promo": "Vibes on vibes 🌊 Afro pop energy all day\n\n#NewMusic #AfroPop #AfroVibes #Mrmakmax",
}

result = {"api_status": {"endpoint": "https://promo-engine-production-74d9.up.railway.app/api/content",
                          "result": "HTTP_404 (Railway app deleted)", "fallback": "direct_mongodb_insert"}}

try:
    client = MongoClient(MONGO_URL, username=MONGO_USERNAME, password=MONGO_PASSWORD,
                         serverSelectionTimeoutMS=15000, connectTimeoutMS=15000)
    client.admin.command("ping")
    db = client[DB_NAME]
    for it in items:
        db.generated_content.insert_one({
            "type": it["type"],
            "file_path": it["file_path"],
            "metadata": it["metadata"],
            "created_at": datetime.utcnow(),
            "used": False,
        })
        print("inserted:", it["type"], "->", it["file_path"].split("\\")[-1])
    # Verify read-back
    latest = list(db.generated_content.find().sort("created_at", -1).limit(5))
    print("\nRead-back (last 5 in DB):")
    for doc in latest:
        print("-", doc["type"], "|", doc["file_path"].split("\\")[-1], "|", doc["created_at"])
    result["api_status"]["mongo_verified"] = True
    result["items"] = items
    result["social_captions"] = social_captions
    client.close()
except Exception as e:
    print("MONGO ERROR:", e)
    result["api_status"]["mongo_verified"] = False
    result["api_status"]["error"] = str(e)
    sys.exit(1)

with open(r"C:\Users\nonamesbeats\promo-engine\data\content_batch_20261001_060104.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print("\nBatch log saved: data/content_batch_20261001_060104.json")
