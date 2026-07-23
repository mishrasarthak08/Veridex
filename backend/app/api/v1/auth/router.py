from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.user import User
from app.core import security
from app.core.config import settings
from app.api.deps import get_current_user
from app.schemas.common import success_response, error_response

router = APIRouter()

from app.schemas.user import UserCreate

@router.post("/register")
async def register_user(
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

@router.post("/login")
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",  # nosec B105
    }

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
async def refresh_access_token(current_user: User = Depends(get_current_user)) -> Any:
    """
    Refresh access token for current user.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        current_user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> Any:
    """
    Logout current user (stateless, so just returns success for client to drop token).
    """
    return success_response(message="Successfully logged out")
