"""Track generated content in MongoDB (direct insert — Railway app deleted).
Batch 20260930_120045 (content factory run of 2026-09-30 12:00 local).
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
BATCH = "20260930_120045"

items = [
    {"type": "fallback_image", "file_path": base + r"\fallback_20260930_120045.png",
     "metadata": {"source": "content_factory_pack", "batch": BATCH}},
    {"type": "quote_card", "file_path": base + r"\quote_20260930_120045_989.png",
     "metadata": {"quote": "Born to make the world dance", "batch": BATCH}},
    {"type": "quote_card", "file_path": base + r"\quote_20260930_120046_8.png",
     "metadata": {"quote": "Afro pop is not just music, it's a vibration", "batch": BATCH}},
    {"type": "promo_banner", "file_path": base + r"\promo_20260930_120046_27.png",
     "metadata": {"title": "NOUVEAU SON DISPONIBLE", "batch": BATCH}},
]

result = {"api_status": {"endpoint": "https://promo-engine-production-74d9.up.railway.app/api/content",
                          "result": "HTTP_404 (Railway app deleted)",
                          "fallback": "direct_mongodb_insert"}}

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
    latest = list(db.generated_content.find({"metadata.batch": BATCH}).sort("created_at", -1).limit(10))
    print("\nRead-back (batch %s):" % BATCH)
    for doc in latest:
        print("-", doc["type"], "|", doc["file_path"].split("\\")[-1], "|", doc["created_at"])
    result["api_status"]["mongo_verified"] = (len(latest) == 4)
    result["items"] = items
    client.close()
except Exception as e:
    print("MONGO ERROR:", e)
    result["api_status"]["mongo_verified"] = False
    result["api_status"]["error"] = str(e)
    sys.exit(1)

out = r"C:\Users\nonamesbeats\promo-engine\data\content_batch_20260930_120045.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print("\nBatch log saved: data/content_batch_20260930_120045.json")
