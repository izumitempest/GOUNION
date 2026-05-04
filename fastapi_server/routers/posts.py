from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, analytics
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("/", response_model=List[schemas.Post])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_post = crud.create_post(db=db, post=post, user_id=current_user.id)
    analytics.track_event(current_user.id, "post_created", {
        "post_id": db_post.id,
        "is_group_post": db_post.group_id is not None
    })
    return db_post

@router.delete("/{post_id}", response_model=schemas.StatusMessage)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    is_staff = current_user.role in ["admin", "moderator"]
    if post.user_id != current_user.id and not is_staff:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    crud.delete_post(db=db, post_id=post_id)
    return {"status": "success", "message": "Post deleted"}

@router.put("/{post_id}", response_model=schemas.Post)
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
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    return crud.update_post(db=db, post_id=post_id, post_update=post_update)

@router.post("/{post_id}/like", response_model=schemas.LikeResponse)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = crud.get_post(db, post_id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    is_liked = crud.like_post(db=db, post=post, user=current_user)
    db.refresh(post)
    
    if is_liked:
        analytics.track_event(current_user.id, "post_liked", {"post_id": post_id})

    return {
        "status": "liked" if is_liked else "unliked",
        "likes_count": len(post.likes),
    }

@router.get("/{post_id}/comments", response_model=List[schemas.Comment])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db, post_id=post_id)

@router.post("/{post_id}/comments", response_model=schemas.Comment)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_comment(db=db, comment=comment, user_id=current_user.id, post_id=post_id)

# Feed router usually separate but can be here
@router.get("/feed", response_model=List[schemas.Post])
def read_feed(
    skip: int = 0,
    limit: int = 50,
    seed: float = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_feed_posts(db, user_id=current_user.id, skip=skip, limit=limit, seed=seed)

@router.post("/{post_id}/view", response_model=schemas.StatusMessage)
def mark_post_viewed(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.mark_post_as_seen(db, user_id=current_user.id, post_id=post_id)
    analytics.track_event(current_user.id, "post_viewed", {"post_id": post_id})
    return {"status": "success", "message": "Post marked as seen"}


