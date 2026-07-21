import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
        if token_data is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # Query user from DB
    result = await db.execute(select(User).where(User.id == token_data))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

from app.services.policy_service import PolicyService
from app.governance.audit import ImmutableAuditLog

def enforce_policy(resource: str, action: str):
    """
    FastAPI dependency factory to enforce OPA-style YAML policies on a route.
    Usage: @router.get("/", dependencies=[Depends(enforce_policy("project", "read"))])
    """
    async def _enforce_policy(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        policy_service = PolicyService()
        decision = await policy_service.evaluate(db, str(current_user.id), resource, action)
        
        audit_log = ImmutableAuditLog()
        await audit_log.log_action(
            tenant_id="default_tenant", # Could extract from current_user or request
            actor=str(current_user.id),
            action=action,
            resource=resource,
            details={"policy_reason": decision.reason},
            decision="ALLOW" if decision.allow else "DENY",
            policy_id=decision.policy_id
        )

        if not decision.allow:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Forbidden by policy: {decision.reason}")
            
        return current_user
        
    return _enforce_policy
