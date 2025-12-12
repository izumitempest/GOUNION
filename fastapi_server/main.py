from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
import os
import shutil
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
SECRET_KEY = os.getenv("SECRET_KEY") # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

from typing import List

@app.get("/posts/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts

@app.get("/feed/", response_model=List[schemas.Post])
def read_feed(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_feed_posts(db, user_id=current_user.id, skip=skip, limit=limit)

@app.post("/posts/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_post(db=db, post=post, user_id=current_user.id)

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    crud.delete_post(db=db, post_id=post_id)
    return {"status": "success", "message": "Post deleted"}

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post_update: schemas.PostUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    return crud.update_post(db=db, post_id=post_id, post_update=post_update)

@app.post("/posts/{post_id}/like")
def like_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    is_liked = crud.like_post(db=db, post=post, user=current_user)
    return {"status": "liked" if is_liked else "unliked", "likes_count": len(post.likes)}

@app.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
def create_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return crud.create_comment(db=db, comment=comment, user_id=current_user.id, post_id=post_id)

@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    comment = crud.get_comment(db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Allow deletion if user owns the comment OR owns the post
    post = crud.get_post(db, post_id=comment.post_id)
    if comment.user_id != current_user.id and (not post or post.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
        
    crud.delete_comment(db=db, comment_id=comment_id)
    return {"status": "success", "message": "Comment deleted"}

@app.post("/friend-request/{receiver_id}", response_model=schemas.FriendRequest)
def send_friend_request(receiver_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    receiver = crud.get_user(db, user_id=receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
        
    existing_request = crud.get_existing_friend_request(db, sender_id=current_user.id, receiver_id=receiver_id)
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
        
    return crud.create_friend_request(db=db, sender_id=current_user.id, receiver_id=receiver_id)

@app.post("/friend-request/{request_id}/accept", response_model=schemas.FriendRequest)
def accept_friend_request(request_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    request = crud.get_friend_request(db, request_id=request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")
        
    if request.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
        
    return crud.update_friend_request_status(db=db, request=request, status="accepted")

@app.post("/friend-request/{request_id}/reject", response_model=schemas.FriendRequest)
def reject_friend_request(request_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    request = crud.get_friend_request(db, request_id=request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")
        
    if request.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
        
    return crud.update_friend_request_status(db=db, request=request, status="rejected")

@app.get("/friends/", response_model=List[schemas.User])
def list_friends(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_friends(db, user_id=current_user.id)

@app.get("/profiles/{username}", response_model=schemas.Profile)
def read_profile(username: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.profile

@app.put("/profiles/me", response_model=schemas.Profile)
def update_profile(profile_update: schemas.ProfileUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.update_profile(db, user_id=current_user.id, profile_update=profile_update)

@app.post("/users/{user_id}/follow")
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    crud.follow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"status": "following"}

@app.post("/users/{user_id}/unfollow")
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    crud.unfollow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"status": "unfollowed"}

@app.get("/users/{user_id}/following", response_model=List[schemas.User])
def get_following(user_id: int, db: Session = Depends(get_db)):
    return crud.get_following(db, user_id=user_id)

@app.get("/users/{user_id}/followers", response_model=List[schemas.User])
def get_followers(user_id: int, db: Session = Depends(get_db)):
    return crud.get_followers(db, user_id=user_id)

@app.get("/search/users", response_model=List[schemas.User])
def search_users(q: str, db: Session = Depends(get_db)):
    return crud.search_users(db, query=q)

@app.get("/search/posts", response_model=List[schemas.Post])
def search_posts(q: str, db: Session = Depends(get_db)):
    return crud.search_posts(db, query=q)

@app.get("/notifications/", response_model=List[schemas.Notification])
def get_notifications(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_notifications(db, user_id=current_user.id)

@app.post("/notifications/read")
def mark_notifications_read(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    crud.mark_notifications_read(db, user_id=current_user.id)
    return {"status": "marked read"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(get_current_user)):
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Upload to Supabase Storage
        bucket_name = "post_images" # Ensure this bucket exists in your Supabase project
        response = supabase.storage.from_(bucket_name).upload(
            path=unique_filename,
            file=file_content,
            file_options={"content-type": file.content_type}
        )
        
        # Get Public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)
        
        return {"filename": unique_filename, "url": public_url}
        
    except Exception as e:
        # Fallback to local storage if Supabase fails
        print(f"Supabase upload failed: {e}. Falling back to local storage.")
        file_path = f"media/{unique_filename}"
        file.file.seek(0) # Reset file pointer
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": unique_filename, "url": f"/media/{unique_filename}"}

@app.get("/university/{university_name}/users", response_model=List[schemas.User])
def get_users_by_university(university_name: str, db: Session = Depends(get_db)):
    return crud.get_users_by_university(db, university_name=university_name)

@app.get("/university/{university_name}/posts", response_model=List[schemas.Post])
def get_posts_by_university(university_name: str, db: Session = Depends(get_db)):
    return crud.get_posts_by_university(db, university_name=university_name)
