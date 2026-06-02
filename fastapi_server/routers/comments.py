from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import asyncio

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/{comment_id}/like", response_model=schemas.LikeResponse)
async def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment_exists = await asyncio.to_thread(crud.get_comment, db, comment_id)
    if not comment_exists:
        raise HTTPException(status_code=404, detail="Comment not found")

    await asyncio.to_thread(crud.like_comment, db, comment_id, current_user.id)
    likes_count = await asyncio.to_thread(crud.get_comment_likes_count, db, comment_id)
    return {"status": "success", "likes_count": likes_count}


@router.delete("/{comment_id}", response_model=schemas.StatusMessage)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = await asyncio.to_thread(crud.get_comment, db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    post_author_id = await asyncio.to_thread(
        lambda: db.query(models.Post.user_id).filter(models.Post.id == comment.post_id).scalar()
    )
    can_delete = (
        comment.user_id == current_user.id
        or post_author_id == current_user.id
        or current_user.role in ["admin", "moderator"]
    )
    if not can_delete:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await asyncio.to_thread(crud.delete_comment, db, comment_id)
    return {"status": "success", "message": "Comment deleted"}
