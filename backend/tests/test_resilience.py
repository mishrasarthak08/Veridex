import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.policy_service import PolicyDecision

@pytest.mark.asyncio
async def test_chaos_injection_endpoint():
    """
    Test that the chaos injection endpoint accepts specific modes and probability.
    """
    with patch('app.core.middleware.jwt.decode', return_value={"sub": "user_123", "tenant_id": "tenant_1"}), \
         patch('app.core.middleware.PolicyService.evaluate', new_callable=AsyncMock) as mock_evaluate:
        
        mock_evaluate.return_value = PolicyDecision(allow=True, reason="Test", policy_id="test")
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/resilience/chaos", 
                json={
                    "mode": "503_error",
                    "probability": 0.8,
                    "duration_ms": 1000
                },
                headers={"Authorization": "Bearer testtoken"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "chaos_injected"
            assert data["mode"] == "503_error"

