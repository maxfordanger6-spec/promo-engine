"""
Action Tracker — Tracks pending, approved, and completed growth actions.
Stores in MongoDB for validation workflow.
"""
import os
import json
import logging
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger("action-tracker")

async def get_db():
    """Reuse the same DB connection pattern."""
    from motor.motor_asyncio import AsyncIOMotorClient
    import os
    
    MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://hermes.enhh09v.mongodb.net/?appName=promo-engine")
    MONGO_USERNAME = os.getenv("MONGO_USERNAME", "le_splash")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "Mignon12345six")
    DB_NAME = os.getenv("DB_NAME", "promo_engine")
    
    clean_url = MONGO_URL.split("?")[0] + "?appName=promo-engine"
    client = AsyncIOMotorClient(
        clean_url,
        username=MONGO_USERNAME,
        password=MONGO_PASSWORD,
        serverSelectionTimeoutMS=10000,
    )
    return client[DB_NAME]


async def create_pending_action(action_type: str, target: dict, ready_text: str, platform: str = "instagram") -> dict:
    """Create a pending action for user validation."""
    db = await get_db()
    doc = {
        "action_type": action_type,  # "dm", "comment", "like", "pitch", "collab_dm"
        "target_name": target.get("name", ""),
        "target_handle": target.get("handle", ""),
        "platform": platform,
        "ready_text": ready_text,  # Pre-generated text ready to copy
        "status": "pending",  # pending -> approved -> done
        "created_at": datetime.utcnow(),
        "approved_at": None,
        "done_at": None,
        "metadata": target,
    }
    result = await db.pending_actions.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


async def get_pending_actions(status: str = "pending", limit: int = 20) -> list:
    """Get actions awaiting validation."""
    db = await get_db()
    cursor = db.pending_actions.find({"status": status}).sort("created_at", -1).limit(limit)
    actions = await cursor.to_list(length=limit)
    for a in actions:
        a["_id"] = str(a["_id"])
    return actions


async def approve_action(action_id: str) -> dict:
    """User approves an action — marks it ready to execute."""
    db = await get_db()
    try:
        oid = ObjectId(action_id)
    except Exception:
        return {"error": "Invalid action ID"}
    
    await db.pending_actions.update_one(
        {"_id": oid},
        {"$set": {"status": "approved", "approved_at": datetime.utcnow()}}
    )
    action = await db.pending_actions.find_one({"_id": oid})
    if action:
        action["_id"] = str(action["_id"])
    return action


async def complete_action(action_id: str) -> dict:
    """Mark an action as done."""
    db = await get_db()
    try:
        oid = ObjectId(action_id)
    except Exception:
        return {"error": "Invalid action ID"}
    
    await db.pending_actions.update_one(
        {"_id": oid},
        {"$set": {"status": "done", "done_at": datetime.utcnow()}}
    )
    return {"status": "ok", "action_id": action_id}


async def approve_all_pending() -> dict:
    """Approve all pending actions at once."""
    db = await get_db()
    result = await db.pending_actions.update_many(
        {"status": "pending"},
        {"$set": {"status": "approved", "approved_at": datetime.utcnow()}}
    )
    return {"approved_count": result.modified_count}


async def get_daily_summary() -> dict:
    """Get today's action summary."""
    db = await get_db()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    pending = await db.pending_actions.count_documents({"status": "pending"})
    approved = await db.pending_actions.count_documents({"status": "approved"})
    done = await db.pending_actions.count_documents({"status": "done"})
    
    return {
        "date": today,
        "pending": pending,
        "approved": approved,
        "done_today": done,
    }


async def generate_batch_from_targeting(targeting_data: dict) -> list:
    """Generate pending actions from a targeting report."""
    actions = []
    
    # Generate DM actions for artists
    for artist in targeting_data.get("targets_artists", [])[:3]:  # Max 3 DMs
        profile = artist.get("profile_url", f"https://instagram.com/{artist.get('handle','').replace('@','')}")
        dm_text = f"""Salut {artist['name']} ! Je suis Mrmakmax, artiste afro pop.

J'ai découvert ta musique via {artist.get('notable', 'les réseaux')} et franchement ça m'a touché. Ton style afro pop me parle grave.

Je bosse sur un projet en ce moment et j'adorerais avoir ton avis. Si t'es open, je peux t'envoyer une démo !

🔗 Son profil : {profile}

Keep pushing 🚀"""

        action = await create_pending_action(
            action_type="dm",
            target=artist,
            ready_text=dm_text,
            platform=artist.get("platform", "instagram"),
        )
        actions.append(action)
    
    # Generate comment actions for curators
    for curator in targeting_data.get("targets_curators", [])[:3]:
        profile = curator.get("profile_url", f"https://instagram.com/{curator.get('handle','').replace('@','')}")
        comment_text = f"""🔥 Gros respect pour le taf que vous faites pour la scène afro ! Je suis Mrmakmax, artiste afro pop — je serais honoré d'être dans votre sélection un jour. Keep pushing la culture 🎵

🔗 Leur page : {profile}"""
        
        action = await create_pending_action(
            action_type="comment",
            target=curator,
            ready_text=comment_text,
            platform=curator.get("platform", "instagram"),
        )
        actions.append(action)
    
    return actions
