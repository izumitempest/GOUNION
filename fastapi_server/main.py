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
    "https://gounion-frontend.onrender.com,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,https://gounion-download.vercel.app,https://localhost,capacitor://localhost,http://localhost"
)
ALLOWED_ORIGINS = [o.strip().rstrip("/") for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
