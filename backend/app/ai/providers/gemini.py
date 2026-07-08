from .base import BaseProvider
import litellm
from typing import List, Dict, Any, AsyncGenerator, Optional

class GeminiProvider(BaseProvider):
    provider_name = "gemini"

    async def generate(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        litellm_model = model if model.startswith("gemini/") else f"gemini/{model}"
        response = await litellm.acompletion(
            model=litellm_model,
            messages=messages,
            tools=tools,
            **kwargs
        )
        return response.model_dump()

    async def stream(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        litellm_model = model if model.startswith("gemini/") else f"gemini/{model}"
        response = await litellm.acompletion(
            model=litellm_model,
            messages=messages,
            tools=tools,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            yield chunk.model_dump()

    def count_tokens(self, model: str, messages: List[Dict[str, Any]]) -> int:
        litellm_model = model if model.startswith("gemini/") else f"gemini/{model}"
        return litellm.token_counter(model=litellm_model, messages=messages)
