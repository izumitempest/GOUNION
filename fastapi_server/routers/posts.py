# posts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models, analytics
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=List[schemas.PostResponse])
async def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return await asyncio.to_thread(crud.get_posts, db, skip, limit)

@router.post("/", response_model=dict)
async def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # crud.create_post_transactional handles commit internally
    db_post_dict = await asyncio.to_thread(crud.create_post_transactional, db, post, current_user.id)
    analytics.track_event(current_user.id, "post_created", {"post_id": db_post_dict["id"]})
    return db_post_dict

@router.delete("/{post_id}", response_model=schemas.StatusMessage)
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    is_staff = current_user.role in ["admin", "moderator"]
    if is_staff:
        success = await asyncio.to_thread(crud.delete_post_administrative_transactional, db, post_id)
    else:
        success = await asyncio.to_thread(crud.delete_post_secure_transactional, db, post_id, current_user.id)
        
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized or post not found")
        
    return {"status": "success", "message": "Post deleted"}

@router.put("/{post_id}", response_model=schemas.StatusMessage)
async def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    success = await asyncio.to_thread(crud.update_post_secure_transactional, db, post_id, current_user.id, post_update)
    if not success:
        raise HTTPException(status_code=403, detail="Not authorized or post not found")
    return {"status": "success", "message": "Post updated"}

@router.post("/{post_id}/like", response_model=schemas.LikeResponse)
async def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    added = await asyncio.to_thread(crud.add_post_like_ultra_performance, db, post_id, current_user.id)
    likes_count = await asyncio.to_thread(crud.get_post_likes_count, db, post_id)
    if not added and likes_count == 0:
        post_exists = await asyncio.to_thread(
            lambda: db.query(models.Post.id).filter(models.Post.id == post_id).first()
        )
        if not post_exists:
            raise HTTPException(status_code=404, detail="Post not found")
    if added:
        analytics.track_event(current_user.id, "post_liked", {"post_id": post_id})
    return {"status": "success", "likes_count": likes_count}

@router.delete("/{post_id}/like", response_model=schemas.StatusMessage)
async def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    removed = await asyncio.to_thread(crud.remove_post_like_transactional, db, post_id, current_user.id)
    return {"status": "success", "message": "Post unliked" if removed else "Like not found"}

@router.get("/{post_id}/comments", response_model=List[dict])
async def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    return await asyncio.to_thread(crud.get_comments, db, post_id)

@router.post("/{post_id}/comments", response_model=dict)
async def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await asyncio.to_thread(crud.create_comment_transactional, db, comment, current_user.id, post_id)

@router.get("/feed", response_model=List[schemas.PostResponse])
async def read_feed(
    skip: int = 0,
    limit: int = 50,
    seed: float = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await asyncio.to_thread(crud.get_feed_posts_optimized, db, current_user.id, skip, limit, seed)

@router.post("/{post_id}/view", response_model=schemas.StatusMessage)
async def mark_post_viewed(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    await asyncio.to_thread(crud.mark_post_as_seen_transactional, db, current_user.id, post_id)
    analytics.track_event(current_user.id, "post_viewed", {"post_id": post_id})
    return {"status": "success", "message": "Post marked as seen"}
