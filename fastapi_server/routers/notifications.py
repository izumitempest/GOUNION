from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user
from ..analytics import track_event

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=List[schemas.Notification])
async def get_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get all notifications for the current user."""
    return await asyncio.to_thread(crud.get_notifications, db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get the count of unread notifications."""
    count = await asyncio.to_thread(crud.get_unread_notification_count, db, user_id=current_user.id)
    return {"count": count}


@router.post("/{notification_id}/read", response_model=schemas.StatusMessage)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Mark a specific notification as read."""
    notif = await asyncio.to_thread(crud.mark_notification_read, db, notification_id=notification_id, user_id=current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.commit()
    return {"status": "success", "message": "Notification marked as read"}


@router.post("/read-all", response_model=schemas.StatusMessage)
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Mark all notifications as read."""
    await asyncio.to_thread(crud.mark_notifications_read, db, user_id=current_user.id)
    db.commit()
    return {"status": "success", "message": "All notifications marked as read"}
