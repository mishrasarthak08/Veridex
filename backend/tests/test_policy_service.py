import pytest
import pytest_asyncio
import uuid
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.policy_service import PolicyService

@pytest_asyncio.fixture
async def policy_service():
    service = PolicyService()
    # Mock redis to avoid real connection and event loop issues during unit tests
    service.redis = AsyncMock()
    service.redis.get.return_value = None
    return service

@pytest.mark.asyncio
async def test_policy_engine_deny_by_default(policy_service):
    """
    Test that a random user has no access by default (deny-by-default).
    """
    db_mock = AsyncMock()
    mock_result = MagicMock()
    db_mock.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = None
    
    decision = await policy_service.evaluate(db_mock, str(uuid.uuid4()), "projects", "read")
    assert decision.allow is False
    assert decision.reason == "User not found"

@pytest.mark.asyncio
async def test_policy_engine_owner_access(policy_service):
    """
    Test that an owner has full access.
    """
    db_mock = AsyncMock()
    
    mock_perm = MagicMock()
    mock_perm.resource = "projects"
    mock_perm.action = "write"
    mock_perm.name = "write_projects"
    
    mock_role = MagicMock()
    mock_role.name = "owner"
    mock_role.permissions = [mock_perm]
    
    mock_user = MagicMock()
    mock_user.roles = [mock_role]
    
    mock_result = MagicMock()
    db_mock.execute.return_value = mock_result
    mock_result.scalar_one_or_none.return_value = mock_user
    
    decision = await policy_service.evaluate(db_mock, str(uuid.uuid4()), "projects", "write")
    assert decision.allow is True
    assert "Granted by role: owner" in decision.reason
