from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from supabase import create_client, Client
import asyncio
import os
import httpx
import logging
from .. import schemas, analytics
from ..dependencies import get_db, supabase, SUPABASE_URL, SUPABASE_KEY

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


def get_auth_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    try:
        if "@" not in form_data.username:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be an email address"
            )

        auth_client = get_auth_client()
        response = await asyncio.to_thread(
            auth_client.auth.sign_in_with_password,
            {
                "email": form_data.username,
                "password": form_data.password,
            },
        )
        
        if not response.session:
             raise Exception("No session returned from Supabase")

        analytics.track_event(response.user.id, "login", {"method": "email"})
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        normalized_error = error_msg.lower().replace("_", " ")
        logger.error("[auth] Login failed for %s: %r", form_data.username, e)
        if "invalid login credentials" in normalized_error or "invalid credentials" in normalized_error:
            detail = "Incorrect email or password"
        elif "email not confirmed" in normalized_error or "confirm your email" in normalized_error:
            detail = "Please confirm your email before logging in"
        else:
            detail = "Authentication service unavailable"
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(body: schemas.RefreshTokenRequest):
    try:
        auth_client = get_auth_client()
        response = await asyncio.to_thread(
            auth_client.auth.refresh_session,
            body.refresh_token,
        )

        if not response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "bearer",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("[auth] Session refresh failed: %r", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/forgot-password")
async def forgot_password(body: schemas.ForgotPasswordRequest):
    try:
        frontend_url = os.getenv("FRONTEND_URL", "https://gounion-frontend.onrender.com")
        redirect_url = f"{frontend_url}/#/reset-password"
        await asyncio.to_thread(
            supabase.auth.reset_password_for_email,
            body.email,
            {"redirect_to": redirect_url},
        )
        analytics.track_event(body.email, "password_reset_requested")
    except Exception as e:
        print(f"Forgot password error: {e}")
    return {"message": "If that email is registered, you will receive a reset link shortly."}

@router.post("/reset-password")
async def reset_password(body: schemas.ResetPasswordRequest):
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
        
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {body.token}",
                    "apikey": supabase_key,
                },
                json={"password": body.new_password}
            )
            
            if response.status_code >= 400:
                error_detail = "Invalid or expired reset token."
                try:
                    error_data = response.json()
                    error_detail = error_data.get("msg") or error_data.get("message") or error_detail
                except:
                    pass
                raise HTTPException(status_code=400, detail=error_detail)
                
        return {"message": "Password updated successfully. You can now log in."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
