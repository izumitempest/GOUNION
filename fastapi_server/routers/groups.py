from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/", response_model=schemas.Group)
async def create_group(
    group: schemas.GroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await asyncio.to_thread(crud.create_group, db, group=group, creator_id=current_user.id)

@router.get("/", response_model=List[schemas.Group])
async def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    groups = await asyncio.to_thread(crud.get_groups, db, skip=skip, limit=limit)
    payload = []
    for g in groups:
        payload.append({
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "cover_image": g.cover_image,
            "privacy": g.privacy,
            "creator_id": g.creator_id,
            "created_at": g.created_at,
            "is_active": g.is_active,
            "creator": g.creator
        })
    return payload

@router.get("/{group_id}", response_model=schemas.Group)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    group = await asyncio.to_thread(crud.get_group, db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "cover_image": group.cover_image,
        "privacy": group.privacy,
        "creator_id": group.creator_id,
        "created_at": group.created_at,
        "is_active": group.is_active,
        "creator": group.creator
    }

@router.put("/{group_id}", response_model=schemas.StatusMessage)
async def update_group(
    group_id: int,
    cover_image: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = await asyncio.to_thread(crud.get_group, db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only creator can update group")
    await asyncio.to_thread(crud.update_group_settings, db, group_id=group_id, cover_image=cover_image)
    db.commit()
    return {"status": "success", "message": "Group updated"}

@router.get("/{group_id}/members/", response_model=List[schemas.GroupMember])
async def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = await asyncio.to_thread(crud.get_group, db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.privacy in ("private", "secret"):
        is_member = await asyncio.to_thread(crud.is_group_member, db, group_id=group_id, user_id=current_user.id)
        if not is_member:
            raise HTTPException(status_code=403, detail="Not a member")
    
    members = await asyncio.to_thread(crud.get_group_members, db, group_id=group_id)
    payload = []
    for m in members:
        payload.append({
            "id": m.id,
            "group_id": m.group_id,
            "user_id": m.user_id,
            "role": m.role,
            "joined_at": m.joined_at,
            "user": m.user
        })
    return payload

@router.get("/{group_id}/posts/", response_model=List[schemas.Post])
async def list_group_posts(
    group_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = await asyncio.to_thread(crud.get_group, db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.privacy in ("private", "secret"):
        is_member = await asyncio.to_thread(crud.is_group_member, db, group_id=group_id, user_id=current_user.id)
        if not is_member:
            raise HTTPException(status_code=403, detail="Not a member")
    
    posts = await asyncio.to_thread(crud.get_group_posts, db, group_id=group_id, skip=skip, limit=limit)
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
            "user": p.user
        })
    return payload

@router.post("/{group_id}/join", response_model=schemas.StatusMessage)
async def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = await asyncio.to_thread(crud.get_group, db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.privacy == "public":
        await asyncio.to_thread(crud.join_group, db, group_id=group_id, user_id=current_user.id)
        db.commit()
        return {"status": "joined"}
    else:
        await asyncio.to_thread(crud.create_group_request, db, group_id=group_id, user_id=current_user.id)
        db.commit()
        return {"status": "pending"}
