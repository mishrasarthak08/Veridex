import pytest

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/v1/health/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"

@pytest.mark.asyncio
async def test_ready_check(async_client):
    response = await async_client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ready"

@pytest.mark.asyncio
async def test_live_check(async_client):
    response = await async_client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "alive"
