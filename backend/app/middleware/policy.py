import yaml
import re
from fastapi import Request, HTTPException
from app.db.models.user import User
import os

POLICY_FILE = os.path.join(os.path.dirname(__file__), "policies.yaml")

class PolicyEngine:
    def __init__(self):
        self.policies = self._load_policies()

    def _load_policies(self):
        with open(POLICY_FILE, "r") as f:
            data = yaml.safe_load(f)
            return data.get("policies", [])

    def check_access(self, path: str, method: str, user: User) -> bool:
        # Default deny
        allowed = False
        
        # Get user roles (simplified for now, assuming user has an 'is_superuser' or roles list)
        user_roles = ["user"]
        if user.is_superuser:
            user_roles.append("admin")
            
        for policy in self.policies:
            # Check method match
            if policy["method"] != "*" and policy["method"] != method:
                continue
                
            # Check path match
            path_pattern = policy["path"].replace("*", ".*")
            if re.match(f"^{path_pattern}$", path):
                # Check roles match
                if any(role in policy["roles"] for role in user_roles):
                    allowed = True
                    break
                    
        return allowed

policy_engine = PolicyEngine()

async def authorize_request(request: Request, user: User):
    """
    Dependency to check if user is authorized based on policies.yaml
    """
    if not policy_engine.check_access(request.url.path, request.method, user):
        raise HTTPException(status_code=403, detail="Forbidden by policy engine")
