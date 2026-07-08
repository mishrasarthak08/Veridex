import pytest
from app.ai.runtime.agent import AgentRuntime
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_agent_runtime():
    runtime = AgentRuntime()
    
    with patch("app.ai.router.ModelRouter.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = {"choices": [{"message": {"content": "I am an autonomous agent."}}]}
        
        result = await runtime.execute("Who are you?")
        assert result == "I am an autonomous agent."
