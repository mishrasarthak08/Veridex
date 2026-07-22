import litellm
import asyncio
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from .base import BaseEmbedder

class LiteLLMEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "gemini/text-embedding-004", batch_size: int = 100):
        self.model_name = model_name
        self.batch_size = batch_size

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(Exception)
    )
    async def _embed_batch(self, batch: List[str]) -> List[List[float]]:
        response = await litellm.aembedding(
            model=self.model_name,
            input=batch
        )
        return [item["embedding"] for item in response["data"]]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        all_embeddings = []
        # Process in batches to avoid provider payload limits
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = await self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)
            # Optional: Add small sleep between batches if strict rate limits apply
            # await asyncio.sleep(0.5)
            
        return all_embeddings
        
    async def embed_query(self, text: str) -> List[float]:
        batch_embeddings = await self._embed_batch([text])
        return batch_embeddings[0]
