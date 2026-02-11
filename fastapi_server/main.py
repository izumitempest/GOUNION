# main.py

from fastapi import Depends, FastAPI, HTTPException, status, Request
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
import asyncio

models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
# Use environment variable or default to a safer list
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
        # run_in_executor to avoid blocking async loop since supabase-py is sync
        user_response = await asyncio.to_thread(supabase.auth.get_user, token)

        if not user_response.user:
            raise credentials_exception
        supabase_user_id = user_response.user.id
    except Exception:
        raise credentials_exception

    user = await asyncio.to_thread(crud.get_user, db, user_id=supabase_user_id)
    if user is None:
        # If user exists in Supabase but not in our DB (edge case), create them?
        # For now, raise error
        raise credentials_exception
    return user


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        response = await asyncio.to_thread(
            supabase.auth.sign_in_with_password,
            {
                "email": form_data.username,
                "password": form_data.password,
            },
        )
        return {"access_token": response.session.access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"LOGIN FAILED: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_feed_posts(db, user_id=current_user.id, skip=skip, limit=limit)


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


@app.get("/profiles/{username}", response_model=schemas.Profile)
def read_profile(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.profile


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


@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)
):
    # Generate unique filename with user folder
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{current_user.id}/{uuid.uuid4()}.{file_extension}"

    try:
        # Read file content
        file_content = await file.read()

        # Upload to Supabase Storage
        bucket_name = "post_images"  #
        response = await asyncio.to_thread(
            supabase.storage.from_(bucket_name).upload,
            path=unique_filename,
            file=file_content,
            file_options={"content-type": file.content_type},
        )

        # Get Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)

        # Remove trailing ? if present (Supabase bug)
        public_url = public_url.rstrip("?")

        return {"filename": unique_filename, "url": public_url}

    except Exception as e:
        # Fallback to local storage if Supabase fails
        print(f"Supabase upload failed: {e}. Falling back to local storage.")
        os.makedirs(f"media/{current_user.id}", exist_ok=True)
        file_path = f"media/{unique_filename}"
        file.file.seek(0)  # Reset file pointer
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": unique_filename, "url": f"/media/{unique_filename}"}


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


@app.post("/groups/{group_id}/join", response_model=schemas.GroupMember)
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.join_group(db, group_id=group_id, user_id=current_user.id)


@app.get("/groups/{group_id}/members", response_model=List[schemas.GroupMember])
def get_group_members(group_id: int, db: Session = Depends(get_db)):
    return crud.get_group_members(db, group_id=group_id)


@app.get("/groups/{group_id}/posts/", response_model=List[schemas.GroupPost])
def list_group_posts(
    group_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
):
    return crud.get_group_posts(db, group_id=group_id, skip=skip, limit=limit)


@app.post("/groups/{group_id}/posts/", response_model=schemas.GroupPost)
def create_group_post(
    group_id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Check if member
    members = crud.get_group_members(db, group_id=group_id)
    if current_user.id not in [m.user_id for m in members]:
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
def create_message(
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
    return (
        db.query(models.Message)
        .options(joinedload(models.Message.sender))
        .filter(models.Message.id == db_message.id)
        .first()
    )


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


@app.get("/")
async def read_root():
    return {"message": "GoUnion API is running. Visit /docs for documentation."}


# app.mount("/", StaticFiles(directory="Frontend/GoUnion", html=True), name="frontend")
