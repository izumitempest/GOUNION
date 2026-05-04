from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
import asyncio
import logging
import traceback
from supabase import create_client, Client
from . import crud, models
from .database import SessionLocal

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_response = await asyncio.to_thread(supabase.auth.get_user, token)

        if not user_response.user:
            raise credentials_exception
            
        supabase_user_id = user_response.user.id
    except Exception as e:
        logger.error(f"[auth] Supabase verification failed: {str(e)}")
        raise credentials_exception

    try:
        user = await asyncio.to_thread(crud.get_user, db, user_id=supabase_user_id)
        
        if user is None:
            raise credentials_exception
            
        if getattr(user, 'is_active', True) is False:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been suspended."
            )
            
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[auth] Local database lookup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database lookup failed during authentication"
        )

async def get_current_moderator(
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role not in ["moderator", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Moderator access required",
        )
    return current_user

async def get_current_admin(
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Administrator access required",
        )
    return current_user
