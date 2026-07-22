import uuid
from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

class QdrantStore:
    def __init__(self, host: str = "qdrant", port: int = 6333, collection_name: str = "knowledge_base"):
        self.client = AsyncQdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_size = 768 # Default for gemini text-embedding-004

    async def initialize_collection(self):
        exists = await self.client.collection_exists(collection_name=self.collection_name)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )

    async def upsert(self, texts: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]]):
        await self.initialize_collection()
        points = []
        for text, embedding, meta in zip(texts, embeddings, metadata):
            # Enforce schema: Add text into payload
            payload = {"text": text, **meta}
            # Use provided ID or generate a new one
            point_id = meta.get("id", str(uuid.uuid4()))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                )
            )
        
        await self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    async def search(self, query_embedding: List[float], limit: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # A basic wrapper around search
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        query_filter = None
        if filters:
            # Very basic filter mapping for tenant isolation
            conditions = []
            for k, v in filters.items():
                conditions.append(FieldCondition(key=k, match=MatchValue(value=v)))
            query_filter = Filter(must=conditions)
            
        results = await self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=limit,
            with_payload=True
        )
        
        return [{"score": hit.score, "payload": hit.payload, "id": str(hit.id)} for hit in results]
