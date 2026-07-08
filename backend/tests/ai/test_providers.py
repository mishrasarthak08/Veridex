import pytest
from app.ai.providers import ProviderFactory
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_openai_provider():
    provider = ProviderFactory.get_provider("openai")
    
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"id": "chatcmpl-123", "choices": [{"message": {"content": "Hello!"}}]}
        mock_acompletion.return_value = mock_response
        
        response = await provider.generate("gpt-4o", [{"role": "user", "content": "Hi"}])
        assert response["choices"][0]["message"]["content"] == "Hello!"
        mock_acompletion.assert_called_once()
