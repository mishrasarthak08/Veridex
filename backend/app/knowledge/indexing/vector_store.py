import asyncio
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import List, Dict, Any, Optional
import uuid
import httpx

class QdrantVectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "veridex_knowledge"):
        # We use AsyncQdrantClient for non-blocking IO
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = 1536 # For text-embedding-3-small
        
    async def ensure_collection_exists(self):
        """Check if collection exists, create it if missing."""
        try:
            collections = await self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                print(f"Creating Qdrant collection: {self.collection_name}")
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                )
        except Exception as e:
            print(f"Failed to ensure Qdrant collection exists: {e}")
            # We don't raise here strictly to allow the application to boot even if Qdrant is temporarily down.

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def add_vectors(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: List[str] = None):
        """Upsert vectors with metadata and robust retries."""
        if not ids:
            ids = [str(uuid.uuid4()) for _ in vectors]
            
        points = [
            PointStruct(id=vid, vector=vec, payload=payload) 
            for vid, vec, payload in zip(ids, vectors, payloads)
        ]
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def search(
        self, 
        query_vector: List[float], 
        limit: int = 5, 
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search vectors with optional exact-match metadata filtering."""
        
        qdrant_filter = None
        if metadata_filters:
            conditions = []
            for key, value in metadata_filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            if conditions:
                qdrant_filter = Filter(must=conditions)
                
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=qdrant_filter,
            limit=limit
        )
        return [{"id": hit.id, "score": hit.score, "payload": hit.payload} for hit in results]
