from .base import BaseProvider
from typing import List, Dict, Any, AsyncGenerator, Optional
from openai import AsyncOpenAI
import tiktoken
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai
from app.core.config import settings

class OpenAIProvider(BaseProvider):
    provider_name = "openai"

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set in environment or .env file to use OpenAIProvider")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
    )
    async def generate(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        # Strip openai/ prefix if present
        model_name = model.replace("openai/", "") if model.startswith("openai/") else model
        
        req_kwargs = {
            "model": model_name,
            "messages": messages,
            **kwargs
        }
        if tools:
            req_kwargs["tools"] = tools

        response = await self.client.chat.completions.create(**req_kwargs)
        return response.model_dump()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
    )
    async def stream(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        model_name = model.replace("openai/", "") if model.startswith("openai/") else model
        
        req_kwargs = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        if tools:
            req_kwargs["tools"] = tools

        response = await self.client.chat.completions.create(**req_kwargs)
        
        async for chunk in response:
            yield chunk.model_dump()

    def count_tokens(self, model: str, messages: List[Dict[str, Any]]) -> int:
        model_name = model.replace("openai/", "") if model.startswith("openai/") else model
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base for newer/unknown models
            encoding = tiktoken.get_encoding("cl100k_base")
            
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                elif isinstance(value, list):
                    # basic handling for multi-modal list content if necessary, though mostly text for now
                    num_tokens += len(encoding.encode(str(value)))
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
