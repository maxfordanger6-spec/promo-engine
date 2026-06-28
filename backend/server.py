import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx

from core import (
    get_db, get_or_create_artist, get_artist_links,
    add_artist_link, add_email_subscriber, get_subscriber_count,
    save_analytics_snapshot, get_analytics_history,
    save_generated_content,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("promo-engine")

app = FastAPI(title="Mrmakmax Promo Engine", version="1.0.0")

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Static files (frontend build) ===
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "build"
STATIC_EXISTS = STATIC_DIR.exists()

if STATIC_EXISTS:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR / "static")), name="static")


# === Request Models ===
class LinkRequest(BaseModel):
    platform: str
    url: str
    label: Optional[str] = None
    icon: Optional[str] = None


class EmailCaptureRequest(BaseModel):
    email: str
    source: Optional[str] = "landing"


class AnalyticsSnapshot(BaseModel):
    spotify_monthly_listeners: Optional[int] = None
    spotify_followers: Optional[int] = None
    instagram_followers: Optional[int] = None
    tiktok_followers: Optional[int] = None
    youtube_subscribers: Optional[int] = None
    email_subscribers: Optional[int] = None


# === Routes ===

@app.get("/api/artist")
async def get_artist():
    """Get artist profile info"""
    artist = await get_or_create_artist()
    links = await get_artist_links()
    subscriber_count = await get_subscriber_count()
    return {
        "artist": artist,
        "links": links,
        "subscriber_count": subscriber_count,
    }


@app.get("/api/links")
async def list_links():
    """Get all social/music links"""
    return await get_artist_links()


@app.post("/api/links")
async def create_link(link: LinkRequest):
    """Add or update a link"""
    return await add_artist_link(
        platform=link.platform,
        url=link.url,
        label=link.label,
        icon=link.icon,
    )


@app.post("/api/email-capture")
async def capture_email(data: EmailCaptureRequest):
    """Capture fan email"""
    result = await add_email_subscriber(email=data.email, source=data.source)
    count = await get_subscriber_count()
    result["total_subscribers"] = count
    return result


@app.get("/api/subscribers/count")
async def subscriber_count():
    """Get subscriber count"""
    return {"count": await get_subscriber_count()}


@app.get("/api/analytics")
async def get_analytics(days: int = 30):
    """Get analytics history"""
    history = await get_analytics_history(days)
    return {"history": history}


@app.post("/api/analytics")
async def post_analytics(snapshot: AnalyticsSnapshot):
    """Save an analytics snapshot"""
    data = snapshot.model_dump()
    data["email_subscribers"] = await get_subscriber_count()
    await save_analytics_snapshot(data)
    return {"status": "ok", "snapshot": data}


@app.get("/api/content")
async def list_content(limit: int = 20, type: str = None):
    """List generated content"""
    db = await get_db()
    filter = {}
    if type:
        filter["type"] = type
    cursor = db.generated_content.find(filter).sort("created_at", -1).limit(limit)
    items = await cursor.to_list(length=limit)
    for item in items:
        item["_id"] = str(item["_id"])
    return {"content": items}


# === Growth Modules ===

@app.get("/api/targeting/daily")
async def get_daily_targets(level: str = "all"):
    """Get daily engagement targets"""
    try:
        from automation.smart_targeting import generate_daily_targets
        plan = generate_daily_targets(level=level)
        return plan
    except ImportError:
        return {"error": "smart_targeting module not available"}


@app.get("/api/email/sequences")
async def get_email_sequences(type: str = "welcome"):
    """Get email nurture sequences"""
    try:
        from automation.email_nurture import get_sequence, generate_email_report
        if type == "report":
            return generate_email_report()
        return {"sequences": get_sequence(type)}
    except ImportError:
        return {"error": "email_nurture module not available"}


@app.get("/api/playlists/targets")
async def get_playlist_targets(genre: str = "all", difficulty: str = "all"):
    """Get playlist pitching targets"""
    try:
        from automation.playlist_pitcher import get_playlist_targets, generate_pitch_strategy
        if genre == "strategy":
            return generate_pitch_strategy()
        return {"playlists": get_playlist_targets(genre, difficulty)}
    except ImportError:
        return {"error": "playlist_pitcher module not available"}


@app.get("/api/playlists/pitch")
async def generate_pitch(song: str = "Nouveau Son", playlist: str = "", style: str = "personal"):
    """Generate a playlist pitch message"""
    try:
        from automation.playlist_pitcher import generate_pitch
        return {"pitch": generate_pitch(song, playlist, style)}
    except ImportError:
        return {"error": "playlist_pitcher module not available"}


@app.get("/api/collabs/strategy")
async def get_collab_strategy():
    """Get collaboration strategy"""
    try:
        from automation.collab_finder import generate_collab_strategy, suggest_daily_networking, find_collaborators
        return {
            "strategy": generate_collab_strategy(),
            "daily": suggest_daily_networking(),
        }
    except ImportError:
        return {"error": "collab_finder module not available"}


@app.get("/api/collabs/list")
async def list_collaborators(category: str = "all"):
    """List potential collaborators"""
    try:
        from automation.collab_finder import find_collaborators
        return {"collaborators": find_collaborators(category)}
    except ImportError:
        return {"error": "collab_finder module not available"}


@app.get("/api/hashtags/set")
async def get_hashtag_set(platform: str = "instagram", type: str = "new_release"):
    """Get optimized hashtag set"""
    try:
        from automation.hashtag_optimizer import generate_hashtag_set, get_hashtags_for_platform
        return generate_hashtag_set(platform, type)
    except ImportError:
        return {"error": "hashtag_optimizer module not available"}


@app.get("/api/hashtags/trending")
async def get_trending_hashtags():
    """Get trending hashtags in afro pop niche"""
    try:
        from automation.hashtag_optimizer import get_trending_in_niche
        return {"trending": get_trending_in_niche()}
    except ImportError:
        return {"error": "hashtag_optimizer module not available"}


# === Action Tracker (Validation Workflow) ===

@app.get("/api/actions")
async def get_pending_actions(status: str = "pending", limit: int = 20):
    """Get pending/approved/done actions"""
    try:
        from automation.action_tracker import get_pending_actions, get_daily_summary
        if status == "summary":
            return await get_daily_summary()
        return {"actions": await get_pending_actions(status, limit)}
    except ImportError:
        return {"error": "action_tracker module not available"}


@app.post("/api/actions/approve/{action_id}")
async def approve_action(action_id: str):
    """Approve a single action"""
    try:
        from automation.action_tracker import approve_action
        return await approve_action(action_id)
    except ImportError:
        return {"error": "action_tracker module not available"}


@app.post("/api/actions/approve-all")
async def approve_all():
    """Approve all pending actions"""
    try:
        from automation.action_tracker import approve_all_pending
        return await approve_all_pending()
    except ImportError:
        return {"error": "action_tracker module not available"}


@app.post("/api/actions/complete/{action_id}")
async def complete_action(action_id: str):
    """Mark an action as done"""
    try:
        from automation.action_tracker import complete_action
        return await complete_action(action_id)
    except ImportError:
        return {"error": "action_tracker module not available"}


@app.post("/api/actions/generate-from-targeting")
async def generate_actions_from_targeting():
    """Generate pending actions from today's targeting data"""
    try:
        from automation.smart_targeting import generate_daily_targets
        from automation.action_tracker import generate_batch_from_targeting
        targeting = generate_daily_targets()
        actions = await generate_batch_from_targeting(targeting)
        return {"generated": len(actions), "actions": actions}
    except ImportError:
        return {"error": "modules not available"}


@app.get("/api/health")
async def health():
    try:
        db = await get_db()
        await db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "database": str(e)},
        )


# === SPA Catch-all (serve frontend) ===
if STATIC_EXISTS:
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str = ""):
        """Serve React SPA — all non-API routes go to index.html"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(STATIC_DIR / "index.html"))


# === Startup ===
@app.on_event("startup")
async def startup():
    logger.info("Promo Engine starting up...")
    db = await get_db()
    await get_or_create_artist()
    logger.info("Promo Engine ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)), reload=True)
