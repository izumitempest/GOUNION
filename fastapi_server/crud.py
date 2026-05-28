# crud.py
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload, selectinload, aliased
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sqlalchemy import or_, and_, case, extract, func, text, select, exists, delete, update
from . import models, schemas

# --- Transactional Wrapper Utilities ---

def _safe_commit(db: Session):
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

# --- User CRUD ---

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user_transactional(db: Session, user: schemas.UserCreate, supabase_id: str):
    try:
        db_user = models.User(id=supabase_id, username=user.username, email=user.email)
        db.add(db_user)
        db.flush()
        db_profile = models.Profile(user_id=db_user.id)
        db.add(db_profile)
        db.commit()
        return {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "is_active": db_user.is_active,
            "role": db_user.role
        }
    except Exception:
        db.rollback()
        raise

def update_profile_secure_transactional(db: Session, user_id: str, profile_update: schemas.ProfileUpdate):
    try:
        db_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
        if not db_profile: return None

        ALLOWED_MUTATIONS = {
            "bio", "profile_picture", "university", "course", 
            "graduation_year", "relationship_status", "hometown", "birth_date", "cover_photo"
        }
        update_data = profile_update.model_dump(exclude_unset=True)
        
        for key in set(update_data.keys()) & ALLOWED_MUTATIONS:
            setattr(db_profile, key, update_data[key])

        db.commit()
        return {
            "id": db_profile.id,
            "user_id": db_profile.user_id,
            "bio": db_profile.bio,
            "profile_picture": db_profile.profile_picture,
            "university": db_profile.university,
            "course": db_profile.course,
            "graduation_year": db_profile.graduation_year,
            "relationship_status": db_profile.relationship_status,
            "hometown": db_profile.hometown,
            "birth_date": db_profile.birth_date,
            "cover_photo": db_profile.cover_photo
        }
    except Exception:
        db.rollback()
        raise

# --- Post CRUD ---

def create_post_transactional(db: Session, post_data: schemas.PostCreate, user_id: str):
    try:
        db_post = models.Post(**post_data.model_dump(), user_id=user_id)
        db.add(db_post)
        db.commit()
        return {
            "id": db_post.id,
            "caption": db_post.caption,
            "image": db_post.image,
            "video": db_post.video,
            "created_at": db_post.created_at,
            "user_id": db_post.user_id
        }
    except Exception:
        db.rollback()
        raise

def delete_post_secure_transactional(db: Session, post_id: int, user_id: str):
    try:
        result = db.execute(delete(models.Post).where(models.Post.id == post_id, models.Post.user_id == user_id))
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise

def delete_post_administrative_transactional(db: Session, post_id: int):
    try:
        result = db.execute(delete(models.Post).where(models.Post.id == post_id))
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise

def update_post_secure_transactional(db: Session, post_id: int, user_id: str, post_update: schemas.PostUpdate):
    try:
        allowed_fields = {"caption", "image", "video"}
        update_data = {k: v for k, v in post_update.model_dump(exclude_unset=True).items() if k in allowed_fields}
        if not update_data: return False

        stmt = update(models.Post).where(models.Post.id == post_id, models.Post.user_id == user_id).values(**update_data)
        result = db.execute(stmt)
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise

def add_post_like_ultra_performance(db: Session, post_id: int, user_id: str) -> bool:
    try:
        like_stmt = pg_insert(models.post_likes).values(post_id=post_id, user_id=user_id).on_conflict_do_nothing(constraint="uq_post_user_likes")
        like_result = db.execute(like_stmt)
        
        if like_result.rowcount > 0:
            post_author_id = db.query(models.Post.user_id).filter(models.Post.id == post_id).scalar()
            if post_author_id and post_author_id != user_id:
                notif_stmt = pg_insert(models.Notification).values(
                    user_id=post_author_id, sender_id=user_id, type="like", post_id=post_id, is_read=False
                ).on_conflict_do_nothing(constraint="uq_notification_dedup")
                db.execute(notif_stmt)
            db.commit()
            return True
        db.commit()
        return False
    except Exception:
        db.rollback()
        raise

def remove_post_like_transactional(db: Session, post_id: int, user_id: str):
    try:
        result = db.execute(delete(models.post_likes).where(and_(models.post_likes.c.post_id == post_id, models.post_likes.c.user_id == user_id)))
        db.commit()
        return result.rowcount > 0
    except Exception:
        db.rollback()
        raise

# --- Feed Algorithm ---

def get_feed_posts_optimized(db: Session, user_id: str, skip: int = 0, limit: int = 50, seed: float = None):
    if seed is not None:
        try: db.execute(text(f"SELECT setseed({float(seed)})"))
        except Exception: pass

    user_profile = db.query(models.Profile.university).filter(models.Profile.user_id == user_id).first()
    user_university = user_profile[0] if user_profile else None

    follow_alias, friend_alias, seen_alias = aliased(models.Follow), aliased(models.FriendRequest), aliased(models.SeenPost)
    since_24h, since_14d = datetime.now(timezone.utc) - timedelta(days=1), datetime.now(timezone.utc) - timedelta(days=14)

    social_weight = case((models.Post.user_id == user_id, 120), (friend_alias.id.isnot(None), 100), (follow_alias.id.isnot(None), 80), else_=10)
    local_weight = case((models.Profile.university == user_university, 50), else_=0) if user_university else 0
    engagement_boost = func.least(func.count(models.post_likes.c.user_id.distinct()) * 2, 200)
    total_weight = social_weight + local_weight + engagement_boost
    decay_score = total_weight / func.pow((extract('epoch', datetime.now(timezone.utc) - models.Post.created_at) / 3600) + 2, 1.2)

    raw_results = db.query(
            models.Post, func.count(models.post_likes.c.user_id.distinct()).label("likes_count"), func.count(models.Comment.id.distinct()).label("comments_count")
        ).join(models.Profile, models.Post.user_id == models.Profile.user_id).outerjoin(follow_alias, and_(models.Post.user_id == follow_alias.following_id, follow_alias.follower_id == user_id)).outerjoin(friend_alias, and_(friend_alias.status == "accepted", or_(and_(friend_alias.sender_id == user_id, friend_alias.receiver_id == models.Post.user_id), and_(friend_alias.receiver_id == user_id, friend_alias.sender_id == models.Post.user_id)))).outerjoin(seen_alias, and_(models.Post.id == seen_alias.post_id, seen_alias.user_id == user_id, seen_alias.seen_at >= since_24h)).outerjoin(models.post_likes, models.Post.id == models.post_likes.c.post_id).outerjoin(models.Comment, models.Post.id == models.Comment.post_id).options(joinedload(models.Post.user)).filter(seen_alias.post_id.is_(None)).filter(models.Post.created_at >= since_14d).group_by(models.Post.id, models.User.id, models.Profile.id, models.Profile.university, friend_alias.id, follow_alias.id).order_by(decay_score.desc(), models.Post.created_at.desc()).offset(skip).limit(limit).all()

    return [{
        "id": p.id, "caption": p.caption, "image": p.image, "video": p.video, "created_at": p.created_at, "user_id": p.user_id,
        "user": {"id": p.user.id, "username": p.user.username}, "likes_count": l, "comments_count": c
    } for p, l, c in raw_results]

def mark_post_as_seen_transactional(db: Session, user_id: str, post_id: int):
    try:
        db.merge(models.SeenPost(user_id=user_id, post_id=post_id, seen_at=func.now()))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise

# --- Notification & Interaction ---

def mark_notifications_read_transactional(db: Session, user_id: str):
    try:
        db.query(models.Notification).filter(models.Notification.user_id == user_id, models.Notification.is_read == False).update({models.Notification.is_read: True})
        db.commit()
    except Exception:
        db.rollback()
        raise

def create_comment_transactional(db: Session, comment_data: schemas.CommentCreate, user_id: str, post_id: int):
    try:
        db_comment = models.Comment(**comment_data.model_dump(), user_id=user_id, post_id=post_id)
        db.add(db_comment)
        db.flush()
        post_author_id = db.query(models.Post.user_id).filter(models.Post.id == post_id).scalar()
        if post_author_id and post_author_id != user_id:
            db.execute(pg_insert(models.Notification).values(user_id=post_author_id, sender_id=user_id, type="comment", post_id=post_id, is_read=False).on_conflict_do_nothing(constraint="uq_notification_dedup"))
        db.commit()
        return {"id": db_comment.id, "content": db_comment.content, "user_id": db_comment.user_id, "post_id": db_comment.post_id, "created_at": db_comment.created_at}
    except Exception:
        db.rollback()
        raise

# --- Relationship & Group CRUD (Transaction-wrapped) ---

def follow_user_transactional(db: Session, follower_id: str, following_id: str):
    try:
        db.execute(pg_insert(models.Follow).values(follower_id=follower_id, following_id=following_id).on_conflict_do_nothing())
        db.execute(pg_insert(models.Notification).values(user_id=following_id, sender_id=follower_id, type="follow", is_read=False).on_conflict_do_nothing(constraint="uq_notification_dedup"))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise

def unfollow_user_transactional(db: Session, follower_id: str, following_id: str):
    try:
        db.execute(delete(models.Follow).where(and_(models.Follow.follower_id == follower_id, models.Follow.following_id == following_id)))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise

def create_group_transactional(db: Session, group_data: schemas.GroupCreate, creator_id: str):
    try:
        db_group = models.Group(**group_data.model_dump(), creator_id=creator_id)
        db.add(db_group)
        db.flush()
        db.add(models.GroupMember(group_id=db_group.id, user_id=creator_id, role="admin"))
        db.commit()
        return {"id": db_group.id, "name": db_group.name, "description": db_group.description}
    except Exception:
        db.rollback()
        raise

# --- Message & Conversation ---

def is_user_in_conversation(db: Session, user_id: str, conversation_id: int):
    return db.query(exists().where(and_(models.conversation_participants.c.user_id == user_id, models.conversation_participants.c.conversation_id == conversation_id))).scalar()

def get_or_create_direct_conversation(db: Session, user1_id: str, user2_id: str, max_retries: int = 3):
    l_id, h_id = sorted([user1_id, user2_id])
    for attempt in range(max_retries):
        try:
            e_id = db.query(models.conversation_participants.c.conversation_id).join(models.Conversation).filter(models.Conversation.name == None).group_by(models.conversation_participants.c.conversation_id).having(func.count(models.conversation_participants.c.user_id) == 2).having(func.max(case(((models.conversation_participants.c.user_id == l_id), 1), else_=0)) == 1).having(func.max(case(((models.conversation_participants.c.user_id == h_id), 1), else_=0)) == 1).scalar()
            if e_id: return e_id
            with db.begin_nested():
                db_conv = models.Conversation(name=None)
                db.add(db_conv)
                db.flush()
                db.execute(models.conversation_participants.insert(), [{"user_id": l_id, "conversation_id": db_conv.id}, {"user_id": h_id, "conversation_id": db_conv.id}])
            db.commit()
            return db_conv.id
        except IntegrityError:
            db.expire_all()
            if attempt == max_retries - 1: raise RuntimeError("Concurrency limit reached during conversation setup.")
            continue

def create_message_transactional(db: Session, msg: schemas.MessageCreate, sender_id: str, conversation_id: int = None):
    try:
        r_id = conversation_id or msg.conversation_id
        if msg.recipient_id and not r_id:
            r_id = get_or_create_direct_conversation(db, sender_id, msg.recipient_id)
        db_msg = models.Message(content=msg.content, image_url=msg.image_url, video_url=msg.video_url, conversation_id=r_id, sender_id=sender_id)
        db.add(db_msg)
        db.commit()
        return {"id": db_msg.id, "conversation_id": db_msg.conversation_id, "sender_id": db_msg.sender_id, "content": db_msg.content, "created_at": db_msg.created_at}
    except Exception:
        db.rollback()
        raise

# --- Device & Location ---

def register_device_transactional(db: Session, user_id: str, device: schemas.UserDeviceCreate):
    try:
        existing = db.query(models.UserDevice).filter(models.UserDevice.fcm_token == device.fcm_token).first() if device.fcm_token else None
        if existing:
            existing.last_active = datetime.now(timezone.utc)
            for k, v in device.model_dump(exclude_unset=True).items(): setattr(existing, k, v)
        else:
            db.add(models.UserDevice(**device.model_dump(), user_id=user_id))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise

def update_location_transactional(db: Session, user_id: str, loc: schemas.LocationHistoryCreate):
    try:
        db.add(models.LocationHistory(**loc.model_dump(), user_id=user_id))
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise

# --- Getters (Thread-safe read-only) ---

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    res = db.query(models.Post).options(joinedload(models.Post.user)).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    return [{ "id": p.id, "caption": p.caption, "image": p.image, "video": p.video, "created_at": p.created_at, "user": {"id": p.user.id, "username": p.user.username} } for p in res]

def get_messages(db: Session, conversation_id: int, skip: int = 0, limit: int = 50):
    res = db.query(models.Message).options(joinedload(models.Message.sender)).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at.desc()).offset(skip).limit(limit).all()
    return [{"id": m.id, "content": m.content, "sender_id": m.sender_id, "created_at": m.created_at, "sender": {"username": m.sender.username} if m.sender else None} for m in res]

def get_conversations(db: Session, user_id: str):
    res = db.query(models.Conversation).options(selectinload(models.Conversation.participants).joinedload(models.User.profile)).filter(models.Conversation.participants.any(id=user_id)).order_by(models.Conversation.created_at.desc()).all()
    return [{"id": c.id, "name": c.name, "created_at": c.created_at, "participants": [{"id": p.id, "username": p.username} for p in c.participants]} for c in res]

def get_notifications(db: Session, user_id: str, skip: int = 0, limit: int = 50):
    res = db.query(models.Notification).options(joinedload(models.Notification.sender)).filter(models.Notification.user_id == user_id).order_by(models.Notification.created_at.desc()).offset(skip).limit(limit).all()
    return [{"id": n.id, "type": n.type, "created_at": n.created_at, "is_read": n.is_read, "sender": {"username": n.sender.username}} for n in res]

def get_unread_notification_count(db: Session, user_id: str):
    return db.query(func.count(models.Notification.id)).filter(models.Notification.user_id == user_id, models.Notification.is_read == False).scalar()
