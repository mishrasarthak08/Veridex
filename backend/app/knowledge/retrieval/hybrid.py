from typing import List, Dict, Any
from ..embeddings.base import BaseEmbedder
from ..indexing.vector_store import QdrantVectorStore
from ..indexing.sparse_store import BM25SparseStore

class HybridRetriever:
    def __init__(
        self, 
        embedder: BaseEmbedder,
        vector_store: QdrantVectorStore, 
        sparse_store: BM25SparseStore
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.sparse_store = sparse_store

    async def retrieve(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        # 1. Dense Search
        query_vector = await self.embedder.embed_query(query)
        dense_results = await self.vector_store.search(query_vector, limit=limit)
        
        # 2. Sparse Search (BM25)
        sparse_results = self.sparse_store.search(query, limit=limit)
        
        # 3. Reciprocal Rank Fusion (RRF)
        # Combine dense and sparse results using RRF score
        fused_scores = {}
        items = {}
        
        k = 60 # RRF constant
        
        # Add dense scores
        for rank, hit in enumerate(dense_results):
            doc_id = hit["id"]
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))
            items[doc_id] = hit["payload"]
            
        # Add sparse scores
        for rank, hit in enumerate(sparse_results):
            doc_id = hit["id"]
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))
            items[doc_id] = hit
            
        # Sort by fused score
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_results = []
        for doc_id, score in sorted_results[:limit]:
            item = items[doc_id]
            item["hybrid_score"] = score
            final_results.append(item)
            
        return final_results
