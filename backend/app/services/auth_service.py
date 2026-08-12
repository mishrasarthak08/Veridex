from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.repositories.oauth import OAuthAccountRepository
from app.repositories.audit import AuditRepository
from app.db.models.user import User
from app.db.models.oauth import OAuthAccount
from app.core import security
import string
import secrets

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.oauth_repo = OAuthAccountRepository(db)
        self.audit_repo = AuditRepository(db)
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repo.get_by_email(email)

    async def register_user(self, user_in_dict: dict) -> User:
        user_in_dict["hashed_password"] = security.get_password_hash(user_in_dict.pop("password"))
        
        # Sanitize text inputs to prevent stored XSS
        import re
        def sanitize(val):
            if isinstance(val, str):
                return re.sub(r'<[^>]*>', '', val).strip()
            return val
        
        for field in ("first_name", "last_name"):
            if field in user_in_dict and user_in_dict[field]:
                user_in_dict[field] = sanitize(user_in_dict[field])
        
        # Create user
        user = await self.user_repo.create(user_in_dict)
        
        # Assign the default 'member' role (or 'owner' for bootstrap)
        from sqlalchemy.future import select
        from app.db.models.role import Role
        stmt = select(Role).where(Role.name == "member")
        result = await self.db.execute(stmt)
        default_role = result.scalars().first()
        
        # Fallback to owner if member doesn't exist yet
        if not default_role:
            stmt = select(Role).where(Role.name == "owner")
            result = await self.db.execute(stmt)
            default_role = result.scalars().first()
        
        if default_role:
            from app.db.models.role import user_roles
            from sqlalchemy import insert
            await self.db.execute(insert(user_roles).values(user_id=user.id, role_id=default_role.id))
            await self.db.commit()
            
        return user

    async def log_audit(self, user_id: Optional[str], email: str, ip_address: Optional[str], user_agent: Optional[str], success: bool, failure_reason: Optional[str] = None):
        await self.audit_repo.create({
            "user_id": user_id,
            "email_attempted": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "success": success,
            "failure_reason": failure_reason
        })

    async def verify_login(self, email: str, password: str, ip_address: Optional[str], user_agent: Optional[str]) -> Tuple[Optional[User], Optional[str]]:
        user = await self.get_user_by_email(email)
        
        if not user or not security.verify_password(password, user.hashed_password):
            await self.log_audit(
                str(user.id) if user else None, email, ip_address, user_agent, False, "Incorrect email or password"
            )
            return None, "Incorrect email or password"
            
        if not user.is_active:
            await self.log_audit(
                str(user.id), email, ip_address, user_agent, False, "Inactive user"
            )
            return None, "Inactive user"
            
        return user, None

    async def get_or_create_oauth_user(self, provider: str, provider_account_id: str, primary_email: str, access_token: str, refresh_token: Optional[str] = None, first_name: str = "", last_name: str = "") -> User:
        oauth_account = await self.oauth_repo.get_by_provider(provider, provider_account_id)
        
        if oauth_account:
            # Update tokens
            oauth_account.access_token = access_token
            if refresh_token:
                oauth_account.refresh_token = refresh_token
            await self.oauth_repo.update(oauth_account, {"access_token": access_token, "refresh_token": oauth_account.refresh_token})
            return await self.user_repo.get(oauth_account.user_id)
            
        user = await self.user_repo.get_by_email(primary_email)
        if not user:
            alphabet = string.ascii_letters + string.digits
            random_password = ''.join(secrets.choice(alphabet) for i in range(20))
            user = await self.user_repo.create({
                "email": primary_email,
                "hashed_password": security.get_password_hash(random_password),
                "first_name": first_name,
                "last_name": last_name
            })
            
        await self.oauth_repo.create({
            "user_id": user.id,
            "provider": provider,
            "provider_account_id": provider_account_id,
            "access_token": access_token,
            "refresh_token": refresh_token
        })
        
        return user

    async def update_user(self, user: User, update_data: dict) -> User:
        return await self.user_repo.update(user, update_data)
