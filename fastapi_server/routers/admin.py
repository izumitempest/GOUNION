from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, models, dependencies
from ..dependencies import get_db, get_current_admin, get_current_moderator

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.get_platform_stats(db)

@router.get("/users", response_model=List[schemas.User])
def get_admin_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.get_all_users(db, skip=skip, limit=limit)

@router.put("/users/{user_id}/role", response_model=schemas.StatusMessage)
def update_user_role(
    user_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.update_user_role(db, user_id, role)

@router.post("/users/{user_id}/toggle-active", response_model=schemas.StatusMessage)
def toggle_user_active(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin),
):
    return crud.toggle_user_active(db, user_id)

@router.get("/reports/", response_model=List[schemas.Report])
def get_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator),
):
    return crud.get_reports(db)

@router.post("/reports/{report_id}/resolve", response_model=schemas.StatusMessage)
def resolve_report(
    report_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_moderator),
):
    return crud.resolve_report(db, report_id, status)
