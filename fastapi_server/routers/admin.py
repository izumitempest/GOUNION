from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import asyncio
from .. import crud, schemas, models, dependencies
from ..dependencies import get_db, get_current_admin, get_current_moderator

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return await asyncio.to_thread(crud.get_platform_stats, db)

@router.get("/users", response_model=List[schemas.User])
async def get_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    users = await asyncio.to_thread(crud.get_all_users, db, skip=skip, limit=limit)
    payload = []
    for u in users:
        payload.append({
            "id": u.id,
            "username": u.username,
            "is_active": u.is_active,
            "role": u.role,
            "profile": u.profile
        })
    return payload

@router.put("/users/{user_id}/role", response_model=schemas.StatusMessage)
async def update_user_role(
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    await asyncio.to_thread(crud.update_user_role, db, user_id, role)
    db.commit()
    return {"status": "success", "message": "User role updated"}

@router.post("/users/{user_id}/toggle-active", response_model=schemas.StatusMessage)
async def toggle_user_active(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    await asyncio.to_thread(crud.toggle_user_active, db, user_id)
    db.commit()
    return {"status": "success", "message": "User active status toggled"}

@router.get("/reports/", response_model=List[schemas.Report])
async def get_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator),
):
    reps = await asyncio.to_thread(crud.get_reports, db, skip=skip, limit=limit)
    payload = []
    for r in reps:
        payload.append({
            "id": r.id,
            "user_id": r.user_id,
            "post_id": r.post_id,
            "comment_id": r.comment_id,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at,
            "user": r.user,
            "post": r.post,
            "comment": r.comment
        })
    return payload

@router.post("/reports/{report_id}/resolve", response_model=schemas.StatusMessage)
async def resolve_report(
    report_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator),
):
    await asyncio.to_thread(crud.resolve_report, db, report_id, status)
    db.commit()
    return {"status": "success", "message": "Report resolved"}
