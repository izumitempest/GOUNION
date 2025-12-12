from sqlalchemy.orm import Session
from sqlalchemy import or_
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

def get_profile_by_user_id(db: Session, user_id: int):
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

def update_profile(db: Session, user_id: int, profile_update: schemas.ProfileUpdate):
    db_profile = get_profile_by_user_id(db, user_id)
    if not db_profile:
        return None
    
    update_data = profile_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def get_feed_posts(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # Get friends IDs
    friends = get_friends(db, user_id)
    friend_ids = [f.id for f in friends]
    
    # Get following IDs
    following = get_following(db, user_id)
    following_ids = [f.id for f in following]
    
    # Combine IDs (including self)
    feed_user_ids = list(set(friend_ids + following_ids + [user_id]))
    
    return db.query(models.Post).filter(models.Post.user_id.in_(feed_user_ids)).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate, user_id: int, image_path: str = None):
    db_post = models.Post(**post.dict(), user_id=user_id, image=image_path)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post

def update_post(db: Session, post_id: int, post_update: schemas.PostUpdate):
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    
    update_data = post_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post

def create_notification(db: Session, user_id: int, sender_id: int, type: str, post_id: int = None):
    if user_id == sender_id:
        return # Don't notify self actions
        
    db_notification = models.Notification(
        user_id=user_id,
        sender_id=sender_id,
        type=type,
        post_id=post_id
    )
    db.add(db_notification)
    db.commit()
    return db_notification

def get_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 50):
    return db.query(models.Notification).filter(models.Notification.user_id == user_id).order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()

def mark_notifications_read(db: Session, user_id: int):
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).update({models.Notification.is_read: True})
    db.commit()

def like_post(db: Session, post: models.Post, user: models.User):
    if user in post.likes:
        post.likes.remove(user)
        is_liked = False
    else:
        post.likes.append(user)
        is_liked = True
        create_notification(db, user_id=post.user_id, sender_id=user.id, type="like", post_id=post.id)
    db.commit()
    return is_liked

def create_comment(db: Session, comment: schemas.CommentCreate, user_id: int, post_id: int):
    db_comment = models.Comment(**comment.dict(), user_id=user_id, post_id=post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Get post owner to notify
    post = get_post(db, post_id)
    if post:
        create_notification(db, user_id=post.user_id, sender_id=user_id, type="comment", post_id=post_id)
        
    return db_comment

def get_comment(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment

def get_friend_request(db: Session, request_id: int):
    return db.query(models.FriendRequest).filter(models.FriendRequest.id == request_id).first()

def get_existing_friend_request(db: Session, sender_id: int, receiver_id: int):
    return db.query(models.FriendRequest).filter(
        models.FriendRequest.sender_id == sender_id,
        models.FriendRequest.receiver_id == receiver_id
    ).first()

def create_friend_request(db: Session, sender_id: int, receiver_id: int):
    db_request = models.FriendRequest(sender_id=sender_id, receiver_id=receiver_id, status="pending")
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    create_notification(db, user_id=receiver_id, sender_id=sender_id, type="friend_request")
    return db_request

def update_friend_request_status(db: Session, request: models.FriendRequest, status: str):
    request.status = status
    db.commit()
    db.refresh(request)
    return request

def get_friends(db: Session, user_id: int):
    # Find accepted requests where user is sender or receiver
    requests = db.query(models.FriendRequest).filter(
        or_(models.FriendRequest.sender_id == user_id, models.FriendRequest.receiver_id == user_id),
        models.FriendRequest.status == "accepted"
    ).all()
    
    friend_ids = []
    for req in requests:
        if req.sender_id == user_id:
            friend_ids.append(req.receiver_id)
        else:
            friend_ids.append(req.sender_id)
            
    return db.query(models.User).filter(models.User.id.in_(friend_ids)).all()

def follow_user(db: Session, follower_id: int, following_id: int):
    existing = db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.following_id == following_id
    ).first()
    if existing:
        return existing
    
    db_follow = models.Follow(follower_id=follower_id, following_id=following_id)
    db.add(db_follow)
    db.commit()
    db.refresh(db_follow)
    create_notification(db, user_id=following_id, sender_id=follower_id, type="follow")
    return db_follow

def unfollow_user(db: Session, follower_id: int, following_id: int):
    db.query(models.Follow).filter(
        models.Follow.follower_id == follower_id,
        models.Follow.following_id == following_id
    ).delete()
    db.commit()

def get_following(db: Session, user_id: int):
    follows = db.query(models.Follow).filter(models.Follow.follower_id == user_id).all()
    following_ids = [f.following_id for f in follows]
    return db.query(models.User).filter(models.User.id.in_(following_ids)).all()

def get_followers(db: Session, user_id: int):
    follows = db.query(models.Follow).filter(models.Follow.following_id == user_id).all()
    follower_ids = [f.follower_id for f in follows]
def search_users(db: Session, query: str):
    return db.query(models.User).filter(models.User.username.ilike(f"%{query}%")).all()

def search_posts(db: Session, query: str):
    return db.query(models.Post).filter(models.Post.caption.ilike(f"%{query}%")).all()

def get_users_by_university(db: Session, university_name: str):
    return db.query(models.User).join(models.Profile).filter(models.Profile.university.ilike(f"%{university_name}%")).all()

def get_posts_by_university(db: Session, university_name: str):
    # Get users from that university
    users = get_users_by_university(db, university_name)
    user_ids = [u.id for u in users]
    return db.query(models.Post).filter(models.Post.user_id.in_(user_ids)).order_by(models.Post.created_at.desc()).all()
