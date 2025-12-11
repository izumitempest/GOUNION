from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Create profile
    db_profile = models.Profile(user_id=db_user.id)
    db.add(db_profile)
    db.commit()
    return db_user

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate, user_id: int, image_path: str = None):
    db_post = models.Post(**post.dict(), user_id=user_id, image=image_path)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
