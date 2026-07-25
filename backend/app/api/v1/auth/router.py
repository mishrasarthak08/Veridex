from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.user import User
from app.core import security
from app.core.config import settings
from app.api.deps import get_current_user
from app.schemas.common import success_response, error_response
from app.core.rate_limit import limiter

router = APIRouter()

from app.schemas.user import UserCreate

@router.post("/register")
@limiter.limit("5/minute")
async def register_user(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        tos_accepted=user_in.tos_accepted,
        privacy_accepted=user_in.privacy_accepted,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }

from fastapi.responses import JSONResponse
from app.db.models.audit import LoginAuditLog

@router.post("/login")
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    # Audit logging
    client_host = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        audit_log = LoginAuditLog(
            user_id=str(user.id) if user else None,
            email_attempted=form_data.username,
            ip_address=client_host,
            user_agent=user_agent,
            success=False,
            failure_reason="Incorrect email or password"
        )
        db.add(audit_log)
        await db.commit()
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        audit_log = LoginAuditLog(
            user_id=str(user.id),
            email_attempted=form_data.username,
            ip_address=client_host,
            user_agent=user_agent,
            success=False,
            failure_reason="Inactive user"
        )
        db.add(audit_log)
        await db.commit()
        raise HTTPException(status_code=400, detail="Inactive user")
        
    # MFA Check
    if user.mfa_enabled:
        # User has MFA enabled, return a partial token to hit /login/mfa
        audit_log = LoginAuditLog(
            user_id=str(user.id),
            email_attempted=form_data.username,
            ip_address=client_host,
            user_agent=user_agent,
            success=True,
            failure_reason="MFA required"
        )
        db.add(audit_log)
        await db.commit()
        
        mfa_token = security.create_access_token(
            subject=user.id, expires_delta=timedelta(minutes=5)
        )
        return {"requires_mfa": True, "mfa_token": mfa_token}
    
    # Full login
    audit_log = LoginAuditLog(
        user_id=str(user.id),
        email_attempted=form_data.username,
        ip_address=client_host,
        user_agent=user_agent,
        success=True
    )
    db.add(audit_log)
    await db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    refresh_token = security.create_refresh_token(user.id)
    
    response = JSONResponse(content={
        "access_token": token,
        "token_type": "bearer",
    })
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="strict",
        secure=False, # Set to True in production with HTTPS
    )
    return response

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user profile.
    """
    return success_response(data={
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    })

import httpx
from fastapi.responses import RedirectResponse
from app.db.models.oauth import OAuthAccount
import secrets
import string

@router.get("/github/login")
async def github_login():
    """
    Redirects to GitHub OAuth authorize URL.
    """
    client_id = settings.GITHUB_CLIENT_ID
    if not client_id:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
    
    redirect_uri = "http://localhost:8000/api/v1/auth/github/callback"
    url = f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=user:email"
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Exchanges code for access token, fetches user data, and issues JWT.
    """
    client_id = settings.GITHUB_CLIENT_ID
    client_secret = settings.GITHUB_CLIENT_SECRET
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="GitHub OAuth not configured")
        
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for access token
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
            },
            headers={"Accept": "application/json"}
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")
            
        # 2. Fetch user profile
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        github_user = user_response.json()
        github_id = str(github_user["id"])
        
        # 3. Fetch user email
        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        emails = email_response.json()
        primary_email = next((e["email"] for e in emails if e.get("primary")), None)
        
        if not primary_email:
            raise HTTPException(status_code=400, detail="No primary email found on GitHub account")
            
        # 4. Account Linking / Creation
        # Check if OAuth account exists
        oauth_result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == "github",
                OAuthAccount.provider_account_id == github_id
            )
        )
        oauth_account = oauth_result.scalar_one_or_none()
        
        if oauth_account:
            user_id = oauth_account.user_id
        else:
            # Check if user with email exists
            user_result = await db.execute(select(User).where(User.email == primary_email))
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Create new user
                alphabet = string.ascii_letters + string.digits
                random_password = ''.join(secrets.choice(alphabet) for i in range(20))
                
                user = User(
                    email=primary_email,
                    hashed_password=security.get_password_hash(random_password),
                    first_name=github_user.get("name", "").split(" ")[0] if github_user.get("name") else "",
                    last_name=" ".join(github_user.get("name", "").split(" ")[1:]) if github_user.get("name") else ""
                )
                db.add(user)
                await db.flush() # flush to get user.id
                
            # Create OAuth Account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="github",
                provider_account_id=github_id,
                access_token=access_token
            )
            db.add(oauth_account)
            await db.commit()
            
            user_id = user.id
            
        # 5. Issue JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = security.create_access_token(
            user_id, expires_delta=access_token_expires
        )
        
        return RedirectResponse(url=f"http://localhost:3000/auth/callback?token={jwt_token}")
@router.get("/google/login")
async def google_login():
    """
    Redirects to Google OAuth authorize URL.
    """
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = "http://localhost:8000/api/v1/auth/google/callback"
    scopes = "openid email profile"
    url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&access_type=offline&prompt=consent"
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Exchanges code for Google access and refresh tokens, fetches user data, and issues JWT.
    """
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
    redirect_uri = "http://localhost:8000/api/v1/auth/google/callback"
    
    async with httpx.AsyncClient() as client:
        # 1. Exchange code for access token and refresh token
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        )
        token_data = token_response.json()
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token") # May be None if not prompted
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from Google")
            
        # 2. Fetch user profile
        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        google_user = user_response.json()
        google_id = str(google_user.get("sub"))
        primary_email = google_user.get("email")
        
        if not google_id or not primary_email:
            raise HTTPException(status_code=400, detail="Failed to get user profile from Google")
            
        # 3. Account Linking / Creation
        oauth_result = await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == "google",
                OAuthAccount.provider_account_id == google_id
            )
        )
        oauth_account = oauth_result.scalar_one_or_none()
        
        if oauth_account:
            user_id = oauth_account.user_id
            # Update tokens
            oauth_account.access_token = access_token
            if refresh_token:
                oauth_account.refresh_token = refresh_token
            await db.commit()
        else:
            # Check if user with email exists
            user_result = await db.execute(select(User).where(User.email == primary_email))
            user = user_result.scalar_one_or_none()
            
            if not user:
                # Create new user
                alphabet = string.ascii_letters + string.digits
                random_password = ''.join(secrets.choice(alphabet) for i in range(20))
                
                user = User(
                    email=primary_email,
                    hashed_password=security.get_password_hash(random_password),
                    first_name=google_user.get("given_name", ""),
                    last_name=google_user.get("family_name", "")
                )
                db.add(user)
                await db.flush()
                
            # Create OAuth Account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider="google",
                provider_account_id=google_id,
                access_token=access_token,
                refresh_token=refresh_token
            )
            db.add(oauth_account)
            await db.commit()
            
            user_id = user.id
            
        # 4. Issue JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_token = security.create_access_token(
            user_id, expires_delta=access_token_expires
        )
        
        return RedirectResponse(url=f"http://localhost:3000/auth/callback?token={jwt_token}")

@router.post("/refresh")
async def refresh_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Refresh access token for current user using HttpOnly cookie.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
        
    payload = security.verify_token(refresh_token, "refresh")
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }

import pyotp

@router.post("/mfa/setup")
async def mfa_setup(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Any:
    """
    Generate MFA secret and URI for setup.
    """
    if current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
        
    secret = pyotp.random_base32()
    current_user.mfa_secret = secret
    await db.commit()
    
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name="Veridex")
    
    return {"secret": secret, "uri": uri}

from pydantic import BaseModel
class MFAVerifyRequest(BaseModel):
    code: str

@router.post("/mfa/verify")
async def mfa_verify(request: MFAVerifyRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Any:
    """
    Verify MFA code and enable MFA or issue full tokens if already enabled.
    """
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not setup")
        
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(request.code):
        raise HTTPException(status_code=400, detail="Invalid MFA code")
        
    if not current_user.mfa_enabled:
        current_user.mfa_enabled = True
        await db.commit()
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        current_user.id, expires_delta=access_token_expires
    )
    
    refresh_token = security.create_refresh_token(current_user.id)
    
    response = JSONResponse(content={
        "access_token": token,
        "token_type": "bearer",
    })
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="strict",
        secure=False, # Set to True in production with HTTPS
    )
    return response

@router.post("/logout")
async def logout(response: JSONResponse) -> Any:
    """
    Logout current user.
    """
    resp = JSONResponse(content={"message": "Successfully logged out"})
    resp.delete_cookie("refresh_token")
    return resp
