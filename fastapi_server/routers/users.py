from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models, dependencies, analytics
from ..dependencies import get_db, get_current_user, supabase, logger

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        if crud.get_user_by_username(db, username=user.username):
            raise HTTPException(status_code=400, detail="Username already registered")

        if crud.get_user_by_email(db, email=user.email):
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        auth_response = await asyncio.to_thread(
            supabase.auth.sign_up,
            {"email": user.email, "password": user.password}
        )
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Registration failed. Please try again.")

        supabase_user_id = auth_response.user.id
        
        try:
            db_user = crud.create_user(db=db, user=user, supabase_id=supabase_user_id)
            analytics.identify_user(db_user.id, {
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role
            })
            analytics.track_event(db_user.id, "signup", {"method": "email"})
            return db_user
        except Exception as db_exc:
            logger.error(f"LOCAL DB FAILURE for {supabase_user_id}: {db_exc}. Rolling back Supabase...")
            try:
                await asyncio.to_thread(supabase.auth.admin.delete_user, supabase_user_id)
            except Exception:
                pass
            raise

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/suggestions", response_model=List[schemas.User])
def get_user_suggestions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_suggested_users(db, user_id=current_user.id, limit=limit)


@router.put("/me/profile", response_model=schemas.Profile)
def update_profile(
    profile_update: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.update_profile(db, user_id=current_user.id, profile_update=profile_update)

@router.post("/me/device", response_model=schemas.UserDevice)
def register_device(
    device: schemas.UserDeviceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not device.ip_address:
        device.ip_address = request.client.host
    return crud.register_device(db, user_id=current_user.id, device=device)

@router.post("/me/location", response_model=schemas.LocationHistory)
def update_location(
    location: schemas.LocationHistoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.update_location(db, user_id=current_user.id, location=location)

@router.post("/{user_id}/follow", response_model=schemas.StatusMessage)
def follow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    crud.follow_user(db, follower_id=current_user.id, following_id=user_id)
    analytics.track_event(current_user.id, "user_followed", {"target_user_id": user_id})
    return {"status": "following"}

@router.post("/{user_id}/unfollow", response_model=schemas.StatusMessage)
def unfollow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    crud.unfollow_user(db, follower_id=current_user.id, following_id=user_id)
    return {"status": "unfollowed"}

@router.get("/{user_id}/following", response_model=List[schemas.User])
def get_following(user_id: str, db: Session = Depends(get_db)):
    return crud.get_following(db, user_id=user_id)

@router.get("/{user_id}/followers", response_model=List[schemas.User])
def get_followers(user_id: str, db: Session = Depends(get_db)):
    return crud.get_followers(db, user_id=user_id)

@router.get("/{user_id}/posts", response_model=List[schemas.Post])
def get_user_posts(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return crud.get_user_posts(db, user_id=user_id, skip=skip, limit=limit)
