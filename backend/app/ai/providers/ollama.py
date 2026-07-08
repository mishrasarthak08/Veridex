from .base import BaseProvider
import litellm
from typing import List, Dict, Any, AsyncGenerator, Optional
from app.ai.config import ai_config

class OllamaProvider(BaseProvider):
    provider_name = "ollama"

    @property
    def api_base(self):
        return ai_config.providers.get("ollama", {}).get("base_url", "http://localhost:11434")

    async def generate(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        litellm_model = model if model.startswith("ollama/") else f"ollama/{model}"
        response = await litellm.acompletion(
            model=litellm_model,
            messages=messages,
            tools=tools,
            api_base=self.api_base,
            **kwargs
        )
        return response.model_dump()

    async def stream(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        litellm_model = model if model.startswith("ollama/") else f"ollama/{model}"
        response = await litellm.acompletion(
            model=litellm_model,
            messages=messages,
            tools=tools,
            api_base=self.api_base,
            stream=True,
            **kwargs
        )
        async for chunk in response:
            yield chunk.model_dump()

    def count_tokens(self, model: str, messages: List[Dict[str, Any]]) -> int:
        # litellm token counting for ollama might fallback to default encodings
        litellm_model = model if model.startswith("ollama/") else f"ollama/{model}"
        return litellm.token_counter(model=litellm_model, messages=messages)
