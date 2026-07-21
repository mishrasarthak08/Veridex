import yaml
import os
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import uuid

from app.db.models import User, Role, Permission

class PolicyDecision:
    def __init__(self, allow: bool, policy_id: str, reason: str = ""):
        self.allow = allow
        self.policy_id = policy_id
        self.reason = reason

class PolicyService:
    def __init__(self, policy_dir: str = "app/governance/policies/"):
        self.policy_dir = policy_dir
        self.policies = self._load_policies()

    def _load_policies(self) -> List[Dict[str, Any]]:
        policies = []
        if os.path.exists(self.policy_dir):
            for filename in os.listdir(self.policy_dir):
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    path = os.path.join(self.policy_dir, filename)
                    with open(path, "r") as f:
                        data = yaml.safe_load(f)
                        if data and "policies" in data:
                            policies.extend(data["policies"])
        return policies

    async def _evaluate_condition(self, condition: str, context: Dict[str, Any], db: AsyncSession) -> bool:
        if condition == "true":
            return True
        if condition == "false":
            return False

        # Simple string-based expression evaluator mapped directly to our starter policies
        user = context.get("user")
        
        if condition == "'admin' in user.roles":
            return any(role.name == "admin" for role in user.roles)

        if condition.startswith("user_has_permission"):
            # Expected format: "user_has_permission(user, 'resource', 'action')"
            parts = condition.split(",")
            if len(parts) >= 3:
                res = parts[1].strip().strip("'\"")
                act = parts[2].split(")")[0].strip().strip("'\"")
                
                # Check user roles for permissions
                for role in user.roles:
                    for perm in role.permissions:
                        if (perm.resource == res or perm.resource == "*") and \
                           (perm.action == act or perm.action == "*"):
                            return True
            return False
            
        return False

    async def evaluate(self, db: AsyncSession, user_id: str, resource: str, action: str) -> PolicyDecision:
        # 1. Load user with roles and permissions
        try:
            uid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except ValueError:
            return PolicyDecision(allow=False, policy_id="system", reason="Invalid user ID format")
            
        stmt = select(User).where(User.id == uid).options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            return PolicyDecision(allow=False, policy_id="system", reason="User not found")

        context = {
            "user": user,
            "resource": resource,
            "action": action
        }

        # 2. Evaluate policies in order
        # Look for explicit DENY first
        for policy in self.policies:
            # Check resource/action match
            if policy.get("resource") not in [resource, "*"]:
                continue
            if policy.get("action") not in [action, "*"]:
                continue

            if policy.get("effect") == "deny":
                if await self._evaluate_condition(policy.get("condition", "true"), context, db):
                    return PolicyDecision(allow=False, policy_id=policy.get("id"), reason=policy.get("name"))

        # 3. Look for explicit ALLOW
        for policy in self.policies:
            if policy.get("resource") not in [resource, "*"]:
                continue
            if policy.get("action") not in [action, "*"]:
                continue

            if policy.get("effect") == "allow":
                if await self._evaluate_condition(policy.get("condition", "true"), context, db):
                    return PolicyDecision(allow=True, policy_id=policy.get("id"), reason=policy.get("name"))

        # 4. Default DENY if no allow matched
        return PolicyDecision(allow=False, policy_id="default_deny", reason="No policy matched")
