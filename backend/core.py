from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import os
from datetime import datetime
import logging

logger = logging.getLogger("promo-engine")

# MongoDB — credential-free URL, kwargs for auth (Railway bug workaround)
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://hermes.enhh09v.mongodb.net/?appName=promo-engine")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "le_splash")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Mignon12345six")
DB_NAME = os.getenv("DB_NAME", "promo_engine")

_client: AsyncIOMotorClient = None
_db = None


async def get_db():
    global _client, _db
    if _db is None:
        clean_url = MONGO_URL.split("?")[0] + "?appName=promo-engine"
        _client = AsyncIOMotorClient(
            clean_url,
            username=MONGO_USERNAME,
            password=MONGO_PASSWORD,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
        )
        _db = _client[DB_NAME]
        # Verify connection
        await _client.admin.command("ping")
        logger.info(f"MongoDB connected: {DB_NAME}")

        # Ensure indexes
        await _db.artist_links.create_index("platform", unique=True)
        await _db.email_subscribers.create_index("email", unique=True)
        await _db.generated_content.create_index("created_at")
        await _db.analytics_snapshots.create_index("date", unique=True)

    return _db


# === Models ===

async def get_or_create_artist():
    db = await get_db()
    doc = await db.artist.find_one({"_id": "mrmakmax"})
    if not doc:
        doc = {
            "_id": "mrmakmax",
            "name": "Mrmakmax",
            "bio": "Afro pop singer & co-owner of nonamesbeats. Born to make the world dance.",
            "genre": "Afro Pop",
            "birthdate": "1986-05-09",
            "image_url": "",
            "created_at": datetime.utcnow(),
        }
        await db.artist.insert_one(doc)
    return doc


async def get_artist_links():
    db = await get_db()
    links = await db.artist_links.find().to_list(length=50)
    return links


async def add_artist_link(platform: str, url: str, label: str = None, icon: str = None):
    db = await get_db()
    await db.artist_links.update_one(
        {"platform": platform},
        {"$set": {
            "platform": platform,
            "url": url,
            "label": label or platform,
            "icon": icon or platform.lower(),
            "updated_at": datetime.utcnow(),
        }},
        upsert=True,
    )
    return await db.artist_links.find_one({"platform": platform})


async def add_email_subscriber(email: str, source: str = "landing"):
    db = await get_db()
    try:
        await db.email_subscribers.insert_one({
            "email": email,
            "source": source,
            "subscribed_at": datetime.utcnow(),
            "active": True,
        })
        return {"status": "ok", "message": "Bienvenue dans la famille ! 🔥"}
    except Exception:
        # Duplicate email
        await db.email_subscribers.update_one(
            {"email": email},
            {"$set": {"active": True, "last_seen": datetime.utcnow()}},
        )
        return {"status": "ok", "message": "Tu es déjà dans la famille ! 💜"}


async def get_subscriber_count():
    db = await get_db()
    return await db.email_subscribers.count_documents({"active": True})


async def save_analytics_snapshot(data: dict):
    db = await get_db()
    data["date"] = datetime.utcnow().strftime("%Y-%m-%d")
    await db.analytics_snapshots.update_one(
        {"date": data["date"]},
        {"$set": data},
        upsert=True,
    )


async def get_analytics_history(days: int = 30):
    db = await get_db()
    cursor = db.analytics_snapshots.find().sort("date", -1).limit(days)
    return await cursor.to_list(length=days)


async def save_generated_content(content_type: str, file_path: str, metadata: dict = None):
    db = await get_db()
    await db.generated_content.insert_one({
        "type": content_type,
        "file_path": file_path,
        "metadata": metadata or {},
        "created_at": datetime.utcnow(),
        "used": False,
    })
