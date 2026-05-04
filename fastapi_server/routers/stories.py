from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, analytics
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/stories", tags=["stories"])

@router.get("/feed", response_model=List[schemas.Story])
def read_stories_feed(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_feed_stories(db, user_id=current_user.id)

@router.post("/", response_model=schemas.Story)
def create_story(
    story: schemas.StoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_story = crud.create_story(db=db, story=story, user_id=current_user.id)
    analytics.track_event(current_user.id, "story_created", {"story_id": db_story.id})
    return db_story

@router.post("/{story_id}/view", response_model=schemas.StatusMessage)
def view_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.view_story(db, story_id=story_id, user_id=current_user.id)
    analytics.track_event(current_user.id, "story_viewed", {"story_id": story_id})
    return {"status": "success", "message": "Story marked as viewed"}

@router.post("/{story_id}/like", response_model=schemas.StatusMessage)
def like_story(
    story_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    is_liked = crud.like_story(db, story_id=story_id, user_id=current_user.id)
    if is_liked:
        analytics.track_event(current_user.id, "story_liked", {"story_id": story_id})
    return {"status": "liked" if is_liked else "unliked"}
