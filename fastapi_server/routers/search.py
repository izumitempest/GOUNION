from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/search", tags=["search"])


def _sync_map_search_results(users: List[models.User]) -> List[dict]:
    """Map ORM User objects to dicts matching schemas.User, including full profile."""
    return [{
        "id": u.id,
        "username": u.username,
        "is_active": u.is_active,
        "role": u.role,
        "profile": {
            "id": u.profile.id,
            "user_id": u.profile.user_id,
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


@router.get("/users", response_model=List[schemas.User])
async def search_users(
    q: str = "",
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Search for users by username, bio, or university."""
    users = await asyncio.to_thread(crud.search_users, db, query=q, limit=limit)
    return await asyncio.to_thread(_sync_map_search_results, users)
