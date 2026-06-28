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
