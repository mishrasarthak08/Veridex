from typing import List, Dict, Any
from opentelemetry import trace
from app.knowledge.retrieval.hybrid import HybridRetriever
from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.knowledge.indexing.sparse_store import BM25SparseStore

tracer = trace.get_tracer(__name__)

class RetrievalService:
    def __init__(self):
        self.embedder = LiteLLMEmbedder()
        self.vector_store = QdrantVectorStore()
        self.sparse_store = BM25SparseStore()
        self.retriever = HybridRetriever(self.embedder, self.vector_store, self.sparse_store)

    async def search(self, query: str, tenant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a tenant-isolated hybrid search.
        """
        with tracer.start_as_current_span("hybrid_search") as span:
            span.set_attribute("tenant_id", tenant_id)
            span.set_attribute("query_length", len(query))
            span.set_attribute("limit", limit)
            
            results = await self.retriever.retrieve(query, limit=limit, tenant_id=tenant_id)
            
            span.set_attribute("results_count", len(results))
            return results
