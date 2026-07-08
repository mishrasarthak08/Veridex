import asyncio
from typing import List
from openai import AsyncOpenAI
import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import tiktoken
from .base import BaseEmbedder
from app.core.config import settings

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY must be set to use OpenAIEmbedder")
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        try:
            self.encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def _truncate_text(self, text: str, max_tokens: int = 8191) -> str:
        """Truncate text if it exceeds the model's maximum context length."""
        tokens = self.encoding.encode(text)
        if len(tokens) > max_tokens:
            return self.encoding.decode(tokens[:max_tokens])
        return text

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
    )
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        # Ensure we don't exceed token limits
        safe_texts = [self._truncate_text(t) for t in texts]
        
        # OpenAI supports up to 2048 texts per batch
        batch_size = 2000
        all_embeddings = []
        
        for i in range(0, len(safe_texts), batch_size):
            batch = safe_texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model=self.model_name,
                input=batch
            )
            batch_embeddings = [data.embedding for data in response.data]
            all_embeddings.extend(batch_embeddings)
            
        return all_embeddings
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError))
    )
    async def embed_query(self, text: str) -> List[float]:
        safe_text = self._truncate_text(text)
        response = await self.client.embeddings.create(
            model=self.model_name,
            input=[safe_text]
        )
        return response.data[0].embedding
