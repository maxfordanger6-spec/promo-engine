import os
import asyncio
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
    email: EmailStr
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


class ContentRequest(BaseModel):
    type: str
    file_path: str
    metadata: Optional[dict] = None


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


@app.post("/api/content")
async def create_content(content: ContentRequest):
    """Save generated content"""
    await save_generated_content(
        content_type=content.type,
        file_path=content.file_path,
        metadata=content.metadata,
    )
    return {"status": "ok"}


# === Growth Modules ===
# Helper: call a function from an automation module with graceful fallback

def _auto(mod_name: str, fn, *args, **kwargs):
    """Call fn(*args, **kwargs), returning {"error": ...} if the module is missing."""
    try:
        return fn(*args, **kwargs)
    except ImportError:
        return {"error": f"{mod_name} module not available"}


async def _auto_async(mod_name: str, fn, *args, **kwargs):
    """Like _auto, but awaits the result (for async automation functions)."""
    try:
        result = fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        return result
    except ImportError:
        return {"error": f"{mod_name} module not available"}


@app.get("/api/targeting/daily")
async def get_daily_targets(level: str = "all"):
    from automation.smart_targeting import generate_daily_targets
    return _auto("smart_targeting", generate_daily_targets, level=level)


@app.get("/api/email/sequences")
async def get_email_sequences(type: str = "welcome"):
    from automation.email_nurture import get_sequence, generate_email_report
    if type == "report":
        return _auto("email_nurture", generate_email_report)
    return _auto("email_nurture", lambda: {"sequences": get_sequence(type)})


@app.get("/api/playlists/targets")
async def get_playlist_targets(genre: str = "all", difficulty: str = "all"):
    from automation.playlist_pitcher import get_playlist_targets, generate_pitch_strategy
    if genre == "strategy":
        return _auto("playlist_pitcher", generate_pitch_strategy)
    return _auto("playlist_pitcher", lambda: {"playlists": get_playlist_targets(genre, difficulty)})


@app.get("/api/playlists/pitch")
async def generate_pitch(song: str = "Nouveau Son", playlist: str = "", style: str = "personal"):
    from automation.playlist_pitcher import generate_pitch
    return _auto("playlist_pitcher", lambda: {"pitch": generate_pitch(song, playlist, style)})


@app.get("/api/collabs/strategy")
async def get_collab_strategy():
    from automation.collab_finder import generate_collab_strategy, suggest_daily_networking
    return _auto("collab_finder", lambda: {
        "strategy": generate_collab_strategy(),
        "daily": suggest_daily_networking(),
    })


@app.get("/api/collabs/list")
async def list_collaborators(category: str = "all"):
    from automation.collab_finder import find_collaborators
    return _auto("collab_finder", lambda: {"collaborators": find_collaborators(category)})


@app.get("/api/hashtags/set")
async def get_hashtag_set(platform: str = "instagram", type: str = "new_release"):
    from automation.hashtag_optimizer import generate_hashtag_set
    return _auto("hashtag_optimizer", generate_hashtag_set, platform, type)


@app.get("/api/hashtags/trending")
async def get_trending_hashtags():
    from automation.hashtag_optimizer import get_trending_in_niche
    return _auto("hashtag_optimizer", lambda: {"trending": get_trending_in_niche()})


# === Action Tracker (Validation Workflow) ===

@app.get("/api/actions")
async def get_pending_actions(status: str = "pending", limit: int = 20):
    from automation.action_tracker import get_pending_actions, get_daily_summary
    if status == "summary":
        return await _auto_async("action_tracker", get_daily_summary)
    return await _auto_async("action_tracker", lambda: get_pending_actions(status, limit))


@app.post("/api/actions/approve/{action_id}")
async def approve_action(action_id: str):
    from automation.action_tracker import approve_action as fn
    return await _auto_async("action_tracker", lambda: fn(action_id))


@app.post("/api/actions/approve-all")
async def approve_all():
    from automation.action_tracker import approve_all_pending
    return await _auto_async("action_tracker", approve_all_pending)


@app.post("/api/actions/complete/{action_id}")
async def complete_action(action_id: str):
    from automation.action_tracker import complete_action as fn
    return await _auto_async("action_tracker", lambda: fn(action_id))


@app.post("/api/actions/generate-from-targeting")
async def generate_actions_from_targeting():
    from automation.smart_targeting import generate_daily_targets
    from automation.action_tracker import generate_batch_from_targeting
    targeting = generate_daily_targets()
    actions = await _auto_async("action_tracker", lambda: generate_batch_from_targeting(targeting))
    if isinstance(actions, dict) and "error" in actions:
        return actions
    return {"generated": len(actions), "actions": actions}


# === Daily Digest Email ===

class DigestRequest(BaseModel):
    pending: int = 0
    approved: int = 0
    done_today: int = 0
    to_email: str = "maxfordanger6@gmail.com"


@app.post("/api/email/send-digest")
async def send_daily_digest(data: DigestRequest):
    """Send daily digest email via SMTP (runs on Railway with access to env vars)"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USERNAME", "")
    smtp_pass = os.getenv("SMTP_PASSWORD", "")

    if not smtp_user or not smtp_pass:
        raise HTTPException(status_code=500, detail="SMTP credentials not configured")

    today_str = datetime.utcnow().strftime("%d/%m/%Y")
    subject = f"📊 Mrmakmax Daily — {today_str}"

    body = f"""🔥 Mrmakmax Daily Digest — {today_str}
━━━━━━━━━━━━━━━━━━━━━━━━

📈 STATS DU JOUR
─────────────────
• Actions en attente : {data.pending}
• Actions approuvées (total) : {data.approved}
• Actions complétées aujourd'hui : {data.done_today}

📋 ACTIONS COMPLÉTÉES
─────────────────
Aucune action complétée aujourd'hui.

📌 PLAN POUR DEMAIN
─────────────────
• Traiter les {data.pending} actions en attente
• Maintenir le rythme des validations
• Vérifier les nouveaux followers/engagements

💫 CITATION MOTIVANTE
─────────────────
« Le rythme ne ment jamais. Continue de pousser,
le succès arrive à ceux qui restent constants.
L'afro beat dans le cœur, le business dans la tête. 🥁✨ »

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Daily Digest automatique — Mrmakmax Promo Engine
"""

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = data.to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return {"status": "ok", "message": "Email envoyé avec succès !"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur SMTP: {e}")


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
