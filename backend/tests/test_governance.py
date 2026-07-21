import pytest
import os
import json
import uuid
import aiofiles
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient

from app.db.models import Base, User, Role, Permission
from app.services.policy_service import PolicyService
from app.governance.audit import ImmutableAuditLog
from app.governance.retention import RetentionPolicy
from app.api.deps import enforce_policy

# Setup dummy FastAPI app for testing middleware
app = FastAPI()

# Database setup for tests
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

import pytest_asyncio

@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# We'll use a dependency override for getting current user and DB in tests
async def override_get_current_user():
    # Will be overridden in test
    pass
    
async def override_get_db():
    # Will be overridden in test
    pass

@app.get("/project/read", dependencies=[Depends(enforce_policy("project", "read"))])
async def read_project():
    return {"status": "success"}

@app.get("/connector/invoke", dependencies=[Depends(enforce_policy("connector", "invoke"))])
async def invoke_connector():
    return {"status": "success"}


@pytest_asyncio.fixture
async def setup_governance_db(db_session: AsyncSession):
    """Setup users, roles and permissions for tests."""
    
    # Create permissions
    proj_read_perm = Permission(name="project:read", resource="project", action="read")
    proj_write_perm = Permission(name="project:write", resource="project", action="write")
    
    # Create roles
    admin_role = Role(name="admin", description="Admin role")
    viewer_role = Role(name="viewer", description="Viewer role")
    
    # Assign permissions to roles
    viewer_role.permissions.append(proj_read_perm)
    admin_role.permissions.append(proj_read_perm)
    admin_role.permissions.append(proj_write_perm)
    
    # Create users
    admin_user = User(
        email="admin@test.com", 
        hashed_password="hash", 
        first_name="Admin",
        is_active=True
    )
    admin_user.roles.append(admin_role)
    
    viewer_user = User(
        email="viewer@test.com", 
        hashed_password="hash", 
        first_name="Viewer",
        is_active=True
    )
    viewer_user.roles.append(viewer_role)
    
    db_session.add_all([proj_read_perm, proj_write_perm, admin_role, viewer_role, admin_user, viewer_user])
    await db_session.commit()
    
    return {"admin": admin_user, "viewer": viewer_user}

@pytest.fixture
def audit_log_path(tmp_path):
    return str(tmp_path / "test_audit_trail.jsonl")

@pytest.mark.asyncio
async def test_policy_evaluation_and_audit(setup_governance_db, db_session: AsyncSession, audit_log_path, monkeypatch):
    # Monkeypatch the audit log path globally to ensure we write to a temporary file
    monkeypatch.setattr("app.api.deps.ImmutableAuditLog.__init__", lambda self, log_path=audit_log_path: setattr(self, "log_path", log_path) or None)
    
    users = setup_governance_db
    admin = users["admin"]
    viewer = users["viewer"]
    
    from app.api.deps import get_current_user, get_db

    # Test Viewer accessing allowed resource
    app.dependency_overrides[get_current_user] = lambda: viewer
    app.dependency_overrides[get_db] = lambda: db_session

    client = TestClient(app)
    
    # 1. Viewer trying to read project -> Allowed (has 'project:read' permission)
    response = client.get("/project/read")
    assert response.status_code == 200, f"Expected 200, got {response.status_code} - {response.text}"
    
    # 2. Viewer trying to invoke connector -> Denied (only 'admin' role allowed per YAML policy)
    response = client.get("/connector/invoke")
    assert response.status_code == 403, "Expected 403 Forbidden"
    
    # 3. Admin trying to invoke connector -> Allowed
    app.dependency_overrides[get_current_user] = lambda: admin
    response = client.get("/connector/invoke")
    assert response.status_code == 200, "Expected 200 OK for Admin"
    
    # 4. Verify Audit Logs
    assert os.path.exists(audit_log_path), "Audit log file was not created"
    
    with open(audit_log_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 3, f"Expected 3 audit logs, found {len(lines)}"
        
        log1 = json.loads(lines[0])
        assert log1["decision"] == "ALLOW"
        assert log1["resource"] == "project"
        assert log1["actor"] == str(viewer.id)
        
        log2 = json.loads(lines[1])
        assert log2["decision"] == "DENY"
        assert log2["resource"] == "connector"
        assert log2["actor"] == str(viewer.id)
        
        log3 = json.loads(lines[2])
        assert log3["decision"] == "ALLOW"
        assert log3["resource"] == "connector"
        assert log3["actor"] == str(admin.id)

@pytest.mark.asyncio
async def test_retention_policy_sweeps_logs(audit_log_path):
    # Create some dummy logs
    old_date = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
    recent_date = datetime.now(timezone.utc).isoformat()
    
    logs = [
        {"timestamp": old_date, "action": "test", "decision": "ALLOW"},
        {"timestamp": old_date, "action": "test2", "decision": "DENY"},
        {"timestamp": recent_date, "action": "test3", "decision": "ALLOW"}
    ]
    
    async with aiofiles.open(audit_log_path, "w") as f:
        for log in logs:
            await f.write(json.dumps(log) + "\n")
            
    # Run retention sweep (keep 90 days)
    policy = RetentionPolicy(days_to_retain=90)
    deleted = await policy.sweep_audit_log(audit_log_path)
    
    assert deleted == 2, "Should have deleted 2 old logs"
    
    with open(audit_log_path, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1, "Should have 1 recent log remaining"
        log = json.loads(lines[0])
        assert log["action"] == "test3"
