from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models
from ..dependencies import get_db, get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])

@router.post("/", response_model=schemas.Group)
def create_group(
    group: schemas.GroupCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_group(db, group=group, creator_id=current_user.id)

@router.get("/", response_model=List[schemas.Group])
def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_groups(db, skip=skip, limit=limit)

@router.get("/{group_id}", response_model=schemas.Group)
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/{group_id}", response_model=schemas.Group)
def update_group(
    group_id: int,
    cover_image: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only creator can update group")
    return crud.update_group_settings(db, group_id=group_id, cover_image=cover_image)

@router.get("/{group_id}/members/", response_model=List[schemas.GroupMember])
def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.privacy in ("private", "secret"):
        if not crud.is_group_member(db, group_id=group_id, user_id=current_user.id):
            raise HTTPException(status_code=403, detail="Not a member")
    return crud.get_group_members(db, group_id=group_id)

@router.get("/{group_id}/posts/", response_model=List[schemas.Post])
def list_group_posts(
    group_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group.privacy in ("private", "secret"):
        if not crud.is_group_member(db, group_id=group_id, user_id=current_user.id):
            raise HTTPException(status_code=403, detail="Not a member")
    return crud.get_group_posts(db, group_id=group_id, skip=skip, limit=limit)

@router.post("/{group_id}/join", response_model=schemas.StatusMessage)
def join_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = crud.get_group(db, group_id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.privacy == "public":
        crud.join_group(db, group_id=group_id, user_id=current_user.id)
        return {"status": "joined"}
    else:
        crud.create_group_request(db, group_id=group_id, user_id=current_user.id)
        return {"status": "pending"}
