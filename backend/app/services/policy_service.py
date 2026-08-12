import json
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import uuid

from app.db.models import User, Role, Permission
from app.core.redis_client import redis_client

class PolicyDecision:
    def __init__(self, allow: bool, policy_id: str, reason: str = ""):
        self.allow = allow
        self.policy_id = policy_id
        self.reason = reason

class PolicyService:
    def __init__(self):
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached policy decisions for a specific user."""
        pattern = f"policy:{user_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)

    async def evaluate(self, db: AsyncSession, user_id: str, resource: str, action: str) -> PolicyDecision:
        try:
            uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except ValueError:
            return PolicyDecision(allow=False, policy_id="system", reason="Invalid user ID format")

        cache_key = f"policy:{user_id}:{resource}:{action}"
        
        # 1. Check Redis Cache
        cached_result = await self.redis.get(cache_key)
        if cached_result:
            data = json.loads(cached_result)
            return PolicyDecision(allow=data["allow"], policy_id=data["policy_id"], reason=data["reason"])

        # 2. Cache Miss - Query DB
        # IMPORTANT: Use execution_options to bypass the tenant_id filter.
        # The PolicyService must be able to look up ANY user regardless of
        # the current tenant context, because the middleware sets tenant context
        # BEFORE evaluating the policy, which can hide the user.
        stmt = (
            select(User)
            .where(User.id == uid)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .execution_options(include_all_tenants=True)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return PolicyDecision(allow=False, policy_id="system", reason="User not found")

        # 3. Evaluate RBAC
        allow = False
        reason = "Default Deny"
        policy_id = "rbac_evaluation"

        for role in user.roles:
            for perm in role.permissions:
                if (perm.resource == resource or perm.resource == "*") and \
                   (perm.action == action or perm.action == "*"):
                    allow = True
                    reason = f"Granted by role: {role.name} (Permission: {perm.name})"
                    break
            if allow:
                break

        decision = PolicyDecision(allow=allow, policy_id=policy_id, reason=reason)

        # 4. Cache Result
        await self.redis.set(
            cache_key,
            json.dumps({"allow": decision.allow, "policy_id": decision.policy_id, "reason": decision.reason}),
            ex=self.cache_ttl
        )

        return decision
