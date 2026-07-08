import pytest
from app.ai.router import router
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_router_generate():
    with patch("app.ai.providers.openai.OpenAIProvider.generate", new_callable=AsyncMock) as mock_generate:
        mock_generate.return_value = {"choices": [{"message": {"content": "Routed Hello!"}}], "usage": {"prompt_tokens": 10, "completion_tokens": 10}}
        
        # 'default' routes to gpt-4o which uses openai provider
        res = await router.generate([{"role": "user", "content": "Hi"}], task_type="default")
        assert res["choices"][0]["message"]["content"] == "Routed Hello!"
        mock_generate.assert_called_once()
