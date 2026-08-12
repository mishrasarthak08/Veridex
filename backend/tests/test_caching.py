import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.anthropic import AnthropicProvider
from app.ai.providers.gemini import GeminiProvider

@pytest.fixture(autouse=True)
def mock_settings():
    with patch("app.ai.providers.openai.settings") as mock_settings_openai:
        mock_settings_openai.OPENAI_API_KEY = "test-key"
        yield mock_settings_openai

@pytest.mark.asyncio
async def test_openai_caching_enabled():
    provider = OpenAIProvider()
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"choices": []}
        mock_acompletion.return_value = mock_response
        
        await provider.generate(model="gpt-4o", messages=[{"role": "user", "content": "hello"}])
        
        mock_acompletion.assert_called_once()
        kwargs = mock_acompletion.call_args.kwargs
        assert kwargs.get("caching") is True

@pytest.mark.asyncio
async def test_anthropic_caching_enabled():
    provider = AnthropicProvider()
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"choices": []}
        mock_acompletion.return_value = mock_response
        
        await provider.generate(model="claude-3-haiku-20240307", messages=[{"role": "user", "content": "hello"}])
        
        mock_acompletion.assert_called_once()
        kwargs = mock_acompletion.call_args.kwargs
        assert kwargs.get("caching") is True

@pytest.mark.asyncio
async def test_gemini_caching_enabled():
    provider = GeminiProvider()
    with patch("litellm.acompletion", new_callable=AsyncMock) as mock_acompletion:
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"choices": []}
        mock_acompletion.return_value = mock_response
        
        await provider.generate(model="gemini-1.5-flash", messages=[{"role": "user", "content": "hello"}])
        
        mock_acompletion.assert_called_once()
        kwargs = mock_acompletion.call_args.kwargs
        assert kwargs.get("caching") is True
