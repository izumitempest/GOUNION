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
        username_exists = await asyncio.to_thread(crud.get_user_by_username, db, username=user.username)
        if username_exists:
            raise HTTPException(status_code=400, detail="Username already registered")

        email_exists = await asyncio.to_thread(crud.get_user_by_email, db, email=user.email)
        if email_exists:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        auth_response = await asyncio.to_thread(
            supabase.auth.sign_up,
            {"email": user.email, "password": user.password}
        )
        
        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Registration failed. Please try again.")

        supabase_user_id = auth_response.user.id
        
        try:
            db_user = await asyncio.to_thread(crud.create_user, db=db, user=user, supabase_id=supabase_user_id)
            analytics.identify_user(db_user["id"], {
                "username": db_user["username"],
                "email": db_user["email"],
                "role": db_user["role"]
            })
            analytics.track_event(db_user["id"], "signup", {"method": "email"})
            return db_user
        except Exception as db_exc:
            logger.error(f"LOCAL DB FAILURE for {supabase_user_id}: {db_exc}. Rolling back Supabase...")
            db.rollback()
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

def _sync_map_users(users: List[models.User]) -> List[dict]:
    return [{
        "id": u.id,
        "username": u.username,
        "is_active": u.is_active,
        "role": u.role,
        "profile": {
            "bio": u.profile.bio,
            "profile_picture": u.profile.profile_picture,
            "university": u.profile.university,
            "profile_type": u.profile.profile_type,
            "course": u.profile.course,
            "graduation_year": u.profile.graduation_year,
            "cover_photo": u.profile.cover_photo,
            "relationship_status": u.profile.relationship_status,
            "hometown": u.profile.hometown
        } if u.profile else None
    } for u in users]

@router.get("/suggestions", response_model=List[schemas.User])
async def get_user_suggestions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    users = await asyncio.to_thread(crud.get_suggested_users, db, user_id=current_user.id, limit=limit)
    return await asyncio.to_thread(_sync_map_users, users)


@router.put("/me/profile", response_model=schemas.Profile)
async def update_profile(
    profile_update: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_profile = await asyncio.to_thread(crud.update_profile_secure, db, user_id=current_user.id, profile_update=profile_update)
    if db_profile and "profile_type" not in db_profile:
        db_profile["profile_type"] = "friend"
    return db_profile

@router.post("/me/device", response_model=schemas.UserDevice)
async def register_device(
    device: schemas.UserDeviceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not device.ip_address:
        device.ip_address = request.client.host
    return await asyncio.to_thread(crud.register_device, db, user_id=current_user.id, device=device)

@router.post("/me/location", response_model=schemas.LocationHistory)
async def update_location(
    location: schemas.LocationHistoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await asyncio.to_thread(crud.update_location, db, user_id=current_user.id, location=location)

@router.post("/{user_id}/follow", response_model=schemas.StatusMessage)
async def follow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    await asyncio.to_thread(crud.follow_user, db, follower_id=current_user.id, following_id=user_id)
    db.commit()
    analytics.track_event(current_user.id, "user_followed", {"target_user_id": user_id})
    return {"status": "success", "message": "following"}

@router.post("/{user_id}/unfollow", response_model=schemas.StatusMessage)
async def unfollow_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    await asyncio.to_thread(crud.unfollow_user, db, follower_id=current_user.id, following_id=user_id)
    db.commit()
    return {"status": "success", "message": "unfollowed"}

@router.get("/{user_id}/following", response_model=List[schemas.User])
async def get_following(user_id: str, db: Session = Depends(get_db)):
    users = await asyncio.to_thread(crud.get_following, db, user_id=user_id)
    return await asyncio.to_thread(_sync_map_users, users)

@router.get("/{user_id}/followers", response_model=List[schemas.User])
async def get_followers(user_id: str, db: Session = Depends(get_db)):
    users = await asyncio.to_thread(crud.get_followers, db, user_id=user_id)
    return await asyncio.to_thread(_sync_map_users, users)

@router.get("/{user_id}/posts", response_model=List[schemas.Post])
async def get_user_posts(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    posts = await asyncio.to_thread(crud.get_user_posts, db, user_id=user_id, skip=skip, limit=limit)
    # Mapping to avoid DetachedInstanceError
    payload = []
    for p in posts:
        payload.append({
            "id": p.id,
            "user_id": p.user_id,
            "group_id": p.group_id,
            "image": p.image,
            "video": p.video,
            "caption": p.caption,
            "created_at": p.created_at,
            "user": {
                "id": p.user.id,
                "username": p.user.username,
                "is_active": p.user.is_active,
                "role": p.user.role
            }
        })
    return payload
