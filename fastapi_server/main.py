# main.py

from fastapi import Depends, FastAPI, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os

load_dotenv()

from sqlalchemy.orm import Session, joinedload
from . import crud, models, schemas
from .database import SessionLocal, engine
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
import shutil
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile
from supabase import create_client, Client
import asyncio

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from fastapi.responses import JSONResponse
import traceback
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Exception Handler to catch 500s and ensure CORS headers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_traceback = traceback.format_exc()
    logger.error(f"GLOBAL ERROR: {str(exc)}\n{error_traceback}")
    
    response = JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error_type": type(exc).__name__,
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An unexpected error occurred."
        }
    )
    
    # Manually add CORS headers to ensure the browser doesn't block the error message
    origin = request.headers.get("origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# Pydantic Validation Error Handler
from pydantic import ValidationError
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"VALIDATION ERROR: {exc.json()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

# CORS Configuration
# allow_credentials=True is incompatible with allow_origins=["*"].
# We handle that by always including the frontend origins explicitly.
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "https://gounion-frontend.onrender.com,http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,https://gounion-download.vercel.app"
)
# Parse origins and ensure no trailing slashes, as origins must be exact
ALLOWED_ORIGINS = []
for o in _raw_origins.split(","):
    clean_o = o.strip().rstrip("/")
    if clean_o:
        ALLOWED_ORIGINS.append(clean_o)

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

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
# Mount media directory (fallback)
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")


# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

    async def broadcast_to_conversation(self, message: dict, participant_ids: List[str]):
        for pid in participant_ids:
            if pid in self.active_connections:
                await self.active_connections[pid].send_json(message)

manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# ── Startup migration ──────────────────────────────────────────────────────
# SQLAlchemy create_all only creates missing tables; it won't add new columns
# to existing tables. We handle additive migrations here with IF NOT EXISTS.
@app.on_event("startup")
async def startup_event():
    # 1. Database Migrations
    from .database import engine as _engine, SQLALCHEMY_DATABASE_URL
    if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
        with _engine.connect() as conn:
            try:
                conn.execute(text(
                    "ALTER TABLE posts ADD COLUMN IF NOT EXISTS video VARCHAR;"
                ))
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'user';"
                ))
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;"
                ))
                conn.execute(text(
                    "ALTER TABLE messages ADD COLUMN IF NOT EXISTS image_url VARCHAR;"
                ))
                conn.execute(text(
                    "ALTER TABLE messages ADD COLUMN IF NOT EXISTS video_url VARCHAR;"
                ))
                conn.execute(text(
                    "ALTER TABLE group_members ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'member';"
                ))
                conn.execute(text(
                    "ALTER TABLE groups ADD COLUMN IF NOT EXISTS cover_image VARCHAR;"
                ))
                conn.commit()
                print("[migration] Database schema updated successfully.")
            except Exception as e:
                print(f"[migration] Note: {e}")
    
    # 2. Supabase Connection Check
    try:
        # Simple check to see if we can reach Supabase
        await asyncio.to_thread(supabase.table("users").select("count", count="exact").limit(1).execute)
        print("[startup] Supabase connection verified.")
    except Exception as e:
        print(f"[CRITICAL] Supabase connection failed: {e}")
        # We don't exit, but this will be visible in Render logs


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Auth Configuration
# Auth Configuration
# SECRET_KEY = os.getenv("SECRET_KEY") # Unused, Supabase handles token verification
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Removed create_access_token and verify_password as they are handled by Supabase


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Verify token with Supabase
        logger.info("[auth] Verifying token with Supabase...")
        user_response = await asyncio.to_thread(supabase.auth.get_user, token)

        if not user_response.user:
            logger.warning("[auth] No user found in Supabase session.")
            raise credentials_exception
            
        supabase_user_id = user_response.user.id
        logger.info(f"[auth] Supabase UID verified: {supabase_user_id}")
    except Exception as e:
        logger.error(f"[auth] Supabase verification failed: {str(e)}")
        raise credentials_exception

    try:
        logger.info(f"[auth] Fetching local user data for {supabase_user_id}...")
        user = await asyncio.to_thread(crud.get_user, db, user_id=supabase_user_id)
        
        if user is None:
            logger.warning(f"[auth] User {supabase_user_id} not found in local database.")
            raise credentials_exception
            
        if getattr(user, 'is_active', True) is False:
            logger.warning(f"[auth] Suspended user {user.username} blocked.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended."
            )
            
        logger.info(f"[auth] User {user.username} loaded successfully.")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[auth] Local database lookup failed: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database lookup failed during authentication"
        )


async def get_current_user_optional(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
    db: Session = Depends(get_db),
):
    """Like get_current_user but returns None instead of 401 for unauthenticated requests."""
    if not token:
        return None
    try:
        user_response = await asyncio.to_thread(supabase.auth.get_user, token)
        if not user_response.user:
            return None
        return await asyncio.to_thread(crud.get_user, db, user_id=user_response.user.id)
    except Exception:
        return None


async def get_current_moderator(
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Moderator access required",
        )
    return current_user


async def get_current_admin(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Admin Bootstrap: If no admin exists in the DB, let the current user be one
    admin_exists = db.query(models.User).filter(models.User.role == "admin").first()
    if not admin_exists:
        return current_user

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrator access required",
        )
    return current_user


# Reports
@app.post("/reports/", response_model=schemas.Report)
def create_report(
    report: schemas.ReportCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_report(db, report, user_id=current_user.id)


@app.get("/reports/", response_model=List[schemas.Report])
def get_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator),
):
    return crud.get_reports(db)


@app.post("/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator),
):
    return crud.resolve_report(db, report_id, status)


# Admin Endpoints
@app.get("/admin/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.get_platform_stats(db)


@app.get("/admin/users", response_model=List[schemas.User])
def get_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.get_all_users(db, skip=skip, limit=limit)


@app.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.update_user_role(db, user_id, role)


@app.post("/admin/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.toggle_user_active(db, user_id)


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        # Check if email is valid format
        if "@" not in form_data.username:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be an email address"
            )

        response = await asyncio.to_thread(
            supabase.auth.sign_in_with_password,
            {
                "email": form_data.username,
                "password": form_data.password,
            },
        )
        
        if not response.session:
             raise Exception("No session returned from Supabase")

        return {"access_token": response.session.access_token, "token_type": "bearer"}
    except Exception as e:
        error_msg = str(e)
        print(f"LOGIN FAILED for {form_data.username}: {error_msg}")
        
        # Distinguish between network errors and auth errors
        if "Invalid login credentials" in error_msg:
            detail = "Incorrect email or password"
        elif "Email not confirmed" in error_msg:
            detail = "Please confirm your email before logging in"
        else:
            # Mask technical errors for security, but ensure they are logged on server
            detail = "Authentication service unavailable"
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/auth/forgot-password")
async def forgot_password(body: schemas.ForgotPasswordRequest):
    """Sends a password reset email via Supabase Auth."""
    try:
        frontend_url = os.getenv("FRONTEND_URL", "https://gounion-frontend.onrender.com")
        redirect_url = f"{frontend_url}/reset-password"
        await asyncio.to_thread(
            supabase.auth.reset_password_for_email,
            body.email,
            {"redirect_to": redirect_url},
        )
    except Exception as e:
        # Always return success to prevent email enumeration attacks
        print(f"Forgot password error (non-critical): {e}")
    return {"message": "If that email is registered, you will receive a reset link shortly."}


@app.post("/auth/reset-password")
async def reset_password(body: schemas.ResetPasswordRequest):
    """
    Verifies the access_token from the Supabase reset email redirect and updates the user's password.
    """
    try:
        user_response = await asyncio.to_thread(supabase.auth.get_user, body.token)
        if not user_response.user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token.")

        await asyncio.to_thread(
            supabase.auth.admin.update_user_by_id,
            user_response.user.id,
            {"password": body.new_password},
        )
        return {"message": "Password updated successfully. You can now log in."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username exists locally
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    try:
        # Sign up with Supabase
        auth_response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
            }
        )
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Supabase registration failed")

        # Create user in our DB using Supabase ID
        return crud.create_user(db=db, user=user, supabase_id=auth_response.user.id)

    except Exception as e:
        # If Supabase fails (e.g. email taken), return error
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@app.get("/users/{user_id}/posts", response_model=List[schemas.Post])
def get_user_posts(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Get posts by a specific user — efficient server-side filtering."""
    return crud.get_user_posts(db, user_id=user_id, skip=skip, limit=limit)


@app.post("/users/me/device", response_model=schemas.UserDevice)
def register_device(
    device: schemas.UserDeviceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Auto-fill IP if not provided
    if not device.ip_address:
        device.ip_address = request.client.host
    return crud.register_device(db, user_id=current_user.id, device=device)


@app.post("/users/me/location", response_model=schemas.LocationHistory)
def update_location(
    location: schemas.LocationHistoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.update_location(db, user_id=current_user.id, location=location)


from typing import List


@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts


@app.get("/feed/", response_model=List[schemas.Post])
def read_feed(
    skip: int = 0,
    limit: int = 100,
    reels: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_feed_posts(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        reels=reels,
    )


@app.post("/posts/", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_post(db=db, post=post, user_id=current_user.id)


@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this post"
        )
    crud.delete_post(db=db, post_id=post_id)
    return {"status": "success", "message": "Post deleted"}


@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this post"
        )
    return crud.update_post(db=db, post_id=post_id, post_update=post_update)


@app.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    print(f"LIKE REQUEST: user={current_user.id} post={post_id}")
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    is_liked = crud.like_post(db=db, post=post, user=current_user)
    db.refresh(post)  # Ensure we get updated likes count
    return {
        "status": "liked" if is_liked else "unliked",
        "likes_count": len(post.likes),
    }


@app.get("/posts/{post_id}/comments", response_model=List[schemas.Comment])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db, post_id=post_id)


@app.get("/posts/{post_id}/comments/{comment_id}", response_model=schemas.Comment)
def get_comment(post_id: int, comment_id: int, db: Session = Depends(get_db)):
    return crud.get_comment(db, post_id=post_id, comment_id=comment_id)


@app.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return crud.create_comment(
        db=db, comment=comment, user_id=current_user.id, post_id=post_id
    )


@app.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Allow deletion if user owns the comment OR owns the post
    post = crud.get_post(db, post_id=comment.post_id)
    if comment.user_id != current_user.id and (
        not post or post.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this comment"
        )

    crud.delete_comment(db=db, comment_id=comment_id)
    return {"status": "success", "message": "Comment deleted"}


@app.post("/friend-request/{receiver_id}", response_model=schemas.FriendRequest)
def send_friend_request(
    receiver_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if receiver_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Cannot send friend request to yourself"
        )

    receiver = crud.get_user(db, user_id=receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    existing_request = crud.get_existing_friend_request(
        db, sender_id=current_user.id, receiver_id=receiver_id
    )
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")

    return crud.create_friend_request(
        db=db, sender_id=current_user.id, receiver_id=receiver_id
    )


@app.post("/friend-request/{request_id}/accept", response_model=schemas.FriendRequest)
def accept_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    request = crud.get_friend_request(db, request_id=request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if request.receiver_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to accept this request"
        )

    return crud.update_friend_request_status(db=db, request=request, status="accepted")


@app.post("/friend-request/{request_id}/reject", response_model=schemas.FriendRequest)
def reject_friend_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    request = crud.get_friend_request(db, request_id=request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    if request.receiver_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to reject this request"
        )

    return crud.update_friend_request_status(db=db, request=request, status="rejected")


@app.get("/friends/", response_model=List[schemas.User])
def list_friends(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_friends(db, user_id=current_user.id)


@app.get("/profiles/{username}")
def read_profile(
    username: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user_optional),
):
    user = crud.get_user_by_username(db, username=username)
    if not user or not user.profile:
        raise HTTPException(status_code=404, detail="User not found")

    followers = crud.get_followers(db, user_id=user.id)
    following = crud.get_following(db, user_id=user.id)
    is_following = any(f.id == current_user.id for f in followers) if current_user else False

    profile = user.profile
    return {
        "id": profile.id,
        "user_id": user.id,
        "full_name": profile.bio and user.username,  # fallback
        "bio": profile.bio or "",
        "profile_picture": profile.profile_picture,
        "cover_photo": profile.cover_photo,
        "university": profile.university or "",
        "course": profile.course or "",
        "graduation_year": profile.graduation_year,
        "hometown": profile.hometown or "",
        "relationship_status": profile.relationship_status or "",
        "profile_type": profile.profile_type,
        "username": user.username,
        "email": user.email,
        "followers_count": len(followers),
        "following_count": len(following),
        "is_following": is_following,
    }


@app.put("/profiles/me", response_model=schemas.Profile)
def update_profile(
    profile_update: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.update_profile(
        db, user_id=current_user.id, profile_update=profile_update
    )


@app.post("/users/{user_id}/follow")
def follow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    crud.follow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"status": "following"}


@app.post("/users/{user_id}/unfollow")
def unfollow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.unfollow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"status": "unfollowed"}


@app.get("/users/{user_id}/following", response_model=List[schemas.User])
def get_following(user_id: str, db: Session = Depends(get_db)):
    return crud.get_following(db, user_id=user_id)


@app.get("/users/{user_id}/followers", response_model=List[schemas.User])
def get_followers(user_id: str, db: Session = Depends(get_db)):
    return crud.get_followers(db, user_id=user_id)


@app.get("/search/users", response_model=List[schemas.User])
def search_users(q: str, db: Session = Depends(get_db)):
    return crud.search_users(db, query=q)


@app.get("/search/posts", response_model=List[schemas.Post])
def search_posts(q: str, db: Session = Depends(get_db)):
    return crud.search_posts(db, query=q)


@app.get("/notifications/", response_model=List[schemas.Notification])
def get_notifications(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_notifications(db, user_id=current_user.id)


@app.post("/notifications/read")
def mark_notifications_read(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    crud.mark_notifications_read(db, user_id=current_user.id)
    return {"status": "marked read"}


@app.get("/notifications/unread-count")
def get_unread_count(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    count = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read == False
    ).count()
    return {"count": count}


@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)
):
    import traceback
    file_extension = (file.filename or "bin").split(".")[-1].lower()
    unique_filename = f"{current_user.id}/{uuid.uuid4()}.{file_extension}"
    file_content = await file.read()

    try:
        bucket_name = "post_images"
        print(f"[upload] {unique_filename} | {file.content_type} | {len(file_content)} bytes")

        # Use an isolated admin client because the global 'supabase' client picks up user sessions 
        # during auth endpoints, leading to RLS failures here.
        admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

        response = await asyncio.to_thread(
            admin_supabase.storage.from_(bucket_name).upload,
            path=unique_filename,
            file=file_content,
            file_options={"content-type": file.content_type or "application/octet-stream", "upsert": "true"},
        )
        print(f"[upload] Supabase response: {response}")

        public_url = admin_supabase.storage.from_(bucket_name).get_public_url(unique_filename).rstrip("?")
        print(f"[upload] Public URL: {public_url}")
        return {"filename": unique_filename, "url": public_url}

    except Exception as e:
        print(f"[upload] FAILED: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)} — ensure bucket 'post_images' exists in Supabase Storage and SUPABASE_SERVICE_KEY is set in Render."
        )


@app.get("/university/{university_name}/users", response_model=List[schemas.User])
def get_users_by_university(university_name: str, db: Session = Depends(get_db)):
    return crud.get_users_by_university(db, university_name=university_name)


@app.get("/university/{university_name}/posts", response_model=List[schemas.Post])
def get_posts_by_university(university_name: str, db: Session = Depends(get_db)):
    return crud.get_posts_by_university(db, university_name=university_name)


# Groups
@app.post("/groups/", response_model=schemas.Group)
def create_group(
    group: schemas.GroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_group(db, group=group, creator_id=current_user.id)


@app.get("/groups/", response_model=List[schemas.Group])
def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_groups(db, skip=skip, limit=limit)


@app.get("/groups/{group_id}", response_model=schemas.Group)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@app.put("/groups/{group_id}", response_model=schemas.Group)
def update_group(
    group_id: int,
    cover_image: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only creator can update group")
    return crud.update_group_settings(db, group_id=group_id, cover_image=cover_image)


@app.put("/groups/{group_id}/members/{user_id}/role", response_model=schemas.GroupMember)
def update_group_member_role(
    group_id: int,
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group or group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only admin can change roles")
    return crud.update_group_member_role(db, group_id=group_id, user_id=user_id, role=role)


@app.delete("/groups/{group_id}/members/{user_id}")
def remove_group_member(
    group_id: int,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group or group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only admin can kick members")
    crud.remove_group_member(db, group_id=group_id, user_id=user_id)
    return {"status": "success"}


@app.post("/groups/{group_id}/join", response_model=dict)
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.privacy == "public":
        crud.join_group(db, group_id=group_id, user_id=current_user.id)
        return {"status": "joined", "message": "Successfully joined the group"}
    else:
        # Check if already a member or has a pending request
        members = crud.get_group_members(db, group_id=group_id)
        if current_user.id in [m.user_id for m in members]:
            return {"status": "joined", "message": "Already a member"}

        requests = crud.get_group_requests(db, group_id=group_id)
        if current_user.id in [r.user_id for r in requests]:
            return {"status": "pending", "message": "Request already pending"}

        crud.create_group_request(db, group_id=group_id, user_id=current_user.id)
        return {"status": "pending", "message": "Join request sent to group admins"}


@app.get("/groups/{group_id}/requests/", response_model=List[schemas.GroupRequest])
def list_group_requests(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group or (group.creator_id != current_user.id):
        raise HTTPException(
            status_code=403, detail="Only group admins can see requests"
        )
    return crud.get_group_requests(db, group_id=group_id)


@app.post("/groups/requests/{request_id}/approve")
def approve_group_request(
    request_id: int,
    status: str,  # 'accepted' or 'rejected'
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Get request to find group
    req = (
        db.query(models.GroupRequest)
        .filter(models.GroupRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    group = crud.get_group(db, group_id=req.group_id)
    if not group or group.creator_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Only group admins can approve requests"
        )

    crud.update_group_request_status(db, request_id=request_id, status=status)
    return {"status": "success", "message": f"Request {status}"}


@app.get("/groups/{group_id}/members/", response_model=List[schemas.GroupMember])
def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    # Enforce privacy: private/secret groups require membership
    if group.privacy in ("private", "secret"):
        if not crud.is_group_member(db, group_id=group_id, user_id=current_user.id):
            raise HTTPException(
                status_code=403, detail="You must be a member to view this group's members"
            )
    return crud.get_group_members(db, group_id=group_id)


@app.get("/groups/{group_id}/posts/", response_model=List[schemas.Post])
def list_group_posts(
    group_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    # Enforce privacy: private/secret groups require membership
    if group.privacy in ("private", "secret"):
        if not crud.is_group_member(db, group_id=group_id, user_id=current_user.id):
            raise HTTPException(
                status_code=403, detail="You must be a member to view this group's posts"
            )
    return crud.get_group_posts(db, group_id=group_id, skip=skip, limit=limit)


@app.post("/groups/{group_id}/posts/", response_model=schemas.Post)
def create_group_post(
    group_id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if member
    if not crud.is_group_member(db, group_id=group_id, user_id=current_user.id):
        raise HTTPException(
            status_code=403, detail="Must be a member to post in this group"
        )
    return crud.create_group_post(
        db, group_post=post, group_id=group_id, user_id=current_user.id
    )


# Messaging
@app.get("/conversations/", response_model=List[schemas.Conversation])
def list_conversations(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_conversations(db, user_id=current_user.id)


@app.get("/conversations/{conversation_id}", response_model=schemas.Conversation)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conv = (
        db.query(models.Conversation)
        .options(joinedload(models.Conversation.participants))
        .filter(models.Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # Check if participant
    if current_user.id not in [p.id for p in conv.participants]:
        raise HTTPException(
            status_code=403, detail="Not a participant in this conversation"
        )
    return conv


@app.get(
    "/conversations/{conversation_id}/messages/", response_model=List[schemas.Message]
)
def list_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conv = (
        db.query(models.Conversation)
        .options(joinedload(models.Conversation.participants))
        .filter(models.Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in [p.id for p in conv.participants]:
        raise HTTPException(
            status_code=403, detail="Not a participant in this conversation"
        )
    return (
        db.query(models.Message)
        .options(joinedload(models.Message.sender))
        .filter(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.post("/conversations/{conversation_id}/messages/", response_model=schemas.Message)
async def create_message(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    conv = (
        db.query(models.Conversation)
        .options(joinedload(models.Conversation.participants))
        .filter(models.Conversation.id == conversation_id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if current_user.id not in [p.id for p in conv.participants]:
        raise HTTPException(
            status_code=403, detail="Not a participant in this conversation"
        )
    message.conversation_id = conversation_id  # Ensure it matches

    db_message = crud.create_message(db, message=message, sender_id=current_user.id)
    # Refresh with joinedload for response model
    full_message = (
        db.query(models.Message)
        .options(joinedload(models.Message.sender))
        .filter(models.Message.id == db_message.id)
        .first()
    )
    
    # Broadcast to participants
    if full_message:
        msg_payload = {
            "type": "new_message",
            "message": {
                "id": full_message.id,
                "conversation_id": full_message.conversation_id,
                "content": full_message.content,
                "image_url": full_message.image_url,
                "video_url": full_message.video_url,
                "sender_id": full_message.sender_id,
                "created_at": full_message.created_at.isoformat(),
            }
        }
        # Fire and forget broadcasting
        asyncio.create_task(manager.broadcast_to_conversation(msg_payload, [p.id for p in conv.participants]))

    return full_message


@app.post("/conversations/", response_model=schemas.Conversation)
def create_conversation(
    conversation: schemas.ConversationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Ensure current user is in participants
    if current_user.id not in conversation.participant_ids:
        conversation.participant_ids.append(current_user.id)
    return crud.create_conversation(db, conversation=conversation)


from fastapi.responses import RedirectResponse
from urllib.parse import quote


# Stories
@app.get("/stories/feed", response_model=List[schemas.Story])
def read_stories_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_feed_stories(db, user_id=current_user.id)


@app.post("/stories/", response_model=schemas.Story)
def create_story(
    story: schemas.StoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_story(db=db, story=story, user_id=current_user.id)


@app.post("/stories/{story_id}/view")
def view_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.view_story(db, story_id=story_id, user_id=current_user.id)
    return {"status": "success"}


@app.post("/stories/{story_id}/like")
def like_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    like = crud.like_story(db, story_id=story_id, user_id=current_user.id)
    return {"status": "liked" if like else "unliked"}


@app.get("/")
async def read_root():
    return {
        "message": "GoUnion API is running.",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Diagnostic endpoint to verify backend status and configuration."""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "cors": {
            "allowed_origins": ALLOWED_ORIGINS,
        },
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
