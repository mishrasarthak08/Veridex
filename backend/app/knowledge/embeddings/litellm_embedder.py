import litellm
from typing import List
from .base import BaseEmbedder

class LiteLLMEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # litellm supports batching embeddings out of the box for most providers
        response = await litellm.aembedding(
            model=self.model_name,
            input=texts
        )
        return [item["embedding"] for item in response["data"]]
        
    async def embed_query(self, text: str) -> List[float]:
        response = await litellm.aembedding(
            model=self.model_name,
            input=[text]
        )
        return response["data"][0]["embedding"]
