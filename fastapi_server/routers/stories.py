from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models, analytics
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/stories", tags=["stories"])

@router.get("/feed", response_model=List[schemas.Story])
async def read_stories_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await asyncio.to_thread(crud.get_feed_stories, db, user_id=current_user.id)

@router.post("/", response_model=schemas.Story)
async def create_story(
    story: schemas.StoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_story = await asyncio.to_thread(crud.create_story, db=db, story=story, user_id=current_user.id)
    analytics.track_event(current_user.id, "story_created", {"story_id": db_story["id"]})
    return db_story

@router.post("/{story_id}/view", response_model=schemas.StatusMessage)
async def view_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    await asyncio.to_thread(crud.view_story, db, story_id=story_id, user_id=current_user.id)
    db.commit()
    analytics.track_event(current_user.id, "story_viewed", {"story_id": story_id})
    return {"status": "success", "message": "Story marked as viewed"}

@router.post("/{story_id}/like", response_model=schemas.StatusMessage)
async def like_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    is_liked = await asyncio.to_thread(crud.like_story, db, story_id=story_id, user_id=current_user.id)
    db.commit()
    if is_liked:
        analytics.track_event(current_user.id, "story_liked", {"story_id": story_id})
    return {"status": "success", "message": "liked" if is_liked else "unliked"}
