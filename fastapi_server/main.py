import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from . import migrate
from .routers import auth, users, posts, groups, messages, admin, media, stories

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GoUnion API")

# Startup Migrations
@app.on_event("startup")
async def startup_event():
    migrate.apply_migration()

# CORS Configuration
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://gounion-frontend.onrender.com,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,https://gounion-download.vercel.app"
)
ALLOWED_ORIGINS = [o.strip().rstrip("/") for o in _raw_origins.split(",") if o.strip()]

# Always include mobile webview origins needed by Android APK builds,
# even when ALLOWED_ORIGINS is explicitly set in environment variables.
REQUIRED_MOBILE_ORIGINS = [
    "http://localhost",
    "https://localhost",
    "capacitor://localhost",
    "ionic://localhost",
    "http://10.0.2.2",
    "https://10.0.2.2",
]
for origin in REQUIRED_MOBILE_ORIGINS:
    if origin not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^(https?|capacitor|ionic)://localhost(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_traceback = traceback.format_exc()
    logger.error(f"GLOBAL ERROR: {str(exc)}\n{error_traceback}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error_type": type(exc).__name__,
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An unexpected error occurred."
        }
    )

# Static Files
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(groups.router)
app.include_router(messages.router)
app.include_router(admin.router)
app.include_router(media.router)
app.include_router(stories.router)

@app.get("/")
async def read_root():
    return {
        "message": "GoUnion API is running.",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "has_supabase_url": bool(os.getenv("SUPABASE_URL")),
            "has_supabase_key": bool(os.getenv("SUPABASE_SERVICE_KEY")),
        }
    }


def _parse_version(version: str) -> tuple:
    """Convert dot-separated versions like 2026.04.13.1 into comparable tuples."""
    if not version:
        return (0,)
    normalized = version.replace("-", ".").replace("_", ".")
    parts = []
    for piece in normalized.split("."):
        if piece.isdigit():
            parts.append(int(piece))
        else:
            digits = "".join(ch for ch in piece if ch.isdigit())
            parts.append(int(digits) if digits else 0)
    return tuple(parts or [0])


@app.get("/mobile/version", response_model=schemas.MobileVersionInfo)
async def mobile_version(current_version: Optional[str] = None):
    """
    Returns mobile update metadata.
    - latest_version: latest published APK
    - min_supported_version: minimum app version allowed to continue
    - force_update: true when current version is below minimum supported
    """
    latest_version = os.getenv("MOBILE_LATEST_VERSION", "2026.04.14.1")
    min_supported_version = os.getenv("MOBILE_MIN_SUPPORTED_VERSION", latest_version)
    apk_url = os.getenv(
        "MOBILE_APK_URL",
        f"https://gounion-download.vercel.app/apk/gounion-{quote(latest_version)}.apk?v={quote(latest_version)}",
    )
    release_notes = os.getenv("MOBILE_RELEASE_NOTES")

    current_parsed = _parse_version(current_version or "")
    latest_parsed = _parse_version(latest_version)
    min_supported_parsed = _parse_version(min_supported_version)

    has_update = bool(current_version) and current_parsed < latest_parsed
    force_update = bool(current_version) and current_parsed < min_supported_parsed

    return {
        "latest_version": latest_version,
        "min_supported_version": min_supported_version,
        "apk_url": apk_url,
        "force_update": force_update,
        "has_update": has_update,
        "current_version": current_version,
        "release_notes": release_notes,
    }
