import aiofiles
import json
import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.permission import Permission
from app.services.policy_service import PolicyService

router = APIRouter()

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionAssign(BaseModel):
    name: str
    resource: str
    action: str

@router.get("/")
async def governance_status():
    return {"status": "ok", "message": "Governance service is running"}

@router.get("/policies")
async def get_policies(db: AsyncSession = Depends(get_db)):
    """Return all roles with their associated permissions."""
    stmt = select(Role).options(selectinload(Role.permissions))
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    policies = []
    for r in roles:
        policies.append({
            "role_id": str(r.id),
            "role_name": r.name,
            "permissions": [
                {"id": str(p.id), "name": p.name, "resource": p.resource, "action": p.action}
                for p in r.permissions
            ]
        })
    return policies

@router.get("/roles")
async def get_roles(db: AsyncSession = Depends(get_db)):
    """List all available roles and their permissions."""
    stmt = select(Role)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    
    return [{"id": str(r.id), "name": r.name, "description": r.description} for r in roles]

@router.post("/roles")
async def create_role(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    role = Role(name=role_in.name, description=role_in.description)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return {"id": str(role.id), "name": role.name}

@router.put("/roles/{role_id}/permissions")
async def update_role_permissions(
    role_id: str,
    permissions_in: List[PermissionAssign],
    db: AsyncSession = Depends(get_db)
):
    try:
        r_id = uuid.UUID(role_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role ID")

    # Get Role
    stmt = select(Role).where(Role.id == r_id).options(selectinload(Role.permissions))
    result = await db.execute(stmt)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Resolve or create permissions
    new_perms = []
    for p_in in permissions_in:
        p_stmt = select(Permission).where(
            (Permission.resource == p_in.resource) & 
            (Permission.action == p_in.action)
        )
        p_res = await db.execute(p_stmt)
        perm = p_res.scalar_one_or_none()
        
        if not perm:
            perm = Permission(name=p_in.name, resource=p_in.resource, action=p_in.action)
            db.add(perm)
        
        new_perms.append(perm)
    
    role.permissions = new_perms
    await db.commit()
    return {"status": "ok", "message": f"Updated permissions for role {role.name}"}

@router.post("/users/{user_id}/roles")
async def assign_role_to_user(
    user_id: str,
    role_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    try:
        u_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # IMPORTANT: Need to get user ignoring tenant constraints to assign global roles
    stmt = select(User).where(User.id == u_id).options(selectinload(User.roles)).execution_options(include_all_tenants=True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    roles_to_assign = []
    for rid in role_ids:
        r_stmt = select(Role).where(Role.id == uuid.UUID(rid))
        r_res = await db.execute(r_stmt)
        role = r_res.scalar_one_or_none()
        if role:
            roles_to_assign.append(role)
            
    user.roles = roles_to_assign
    await db.commit()
    
    # Invalidate cache
    svc = PolicyService()
    await svc.invalidate_user_cache(user_id)
    
    return {"status": "ok", "message": f"Updated roles for user {user.email}"}

@router.post("/simulate")
async def simulate_policy(
    request: Request,
    resource: str,
    action: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Simulate a policy decision."""
    service = PolicyService()
    decision = await service.evaluate(db, user_id, resource, action)
    return {
        "allow": decision.allow,
        "policy_id": decision.policy_id,
        "reason": decision.reason
    }

@router.get("/audit-log")
async def get_audit_log(
    request: Request,
    limit: int = Query(50, ge=1, le=1000),
    actor: str = None,
    resource: str = None
) -> List[Dict[str, Any]]:
    """
    Returns the immutable audit log.
    """
    tenant_id = getattr(request.state, "tenant_id", "default_tenant")
    log_path = "audit_trail.jsonl"
    
    if not os.path.exists(log_path):
        return []

    logs = []
    # Simple tail/filtering for JSONL
    async with aiofiles.open(log_path, mode='r') as f:
        async for line in f:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if entry.get("tenant_id") == tenant_id:
                    # Apply filters
                    if actor and entry.get("actor") != actor:
                        continue
                    if resource and entry.get("resource") != resource:
                        continue
                    logs.append(entry)
            except json.JSONDecodeError:
                continue

    # Return newest first, up to limit
    return list(reversed(logs))[-limit:]
