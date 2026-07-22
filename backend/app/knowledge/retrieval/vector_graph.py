from typing import List, Dict, Any
from ..embeddings.base import BaseEmbedder
from ..storage.qdrant_store import QdrantStore
from ..graph.repository import GraphRepository

class VectorGraphRetriever:
    def __init__(
        self, 
        embedder: BaseEmbedder,
        vector_store: QdrantStore, 
        graph_repo: GraphRepository
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.graph_repo = graph_repo

    async def retrieve(self, query: str, limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        # 1. Dense Vector Search
        query_vector = await self.embedder.embed_query(query)
        vector_results = await self.vector_store.search(query_vector, limit=limit, filters=filters)
        
        # 2. Graph Traversal for Context Expansion
        # For each document/chunk retrieved by vector search, pull its connected components in Neo4j
        expanded_results = []
        for hit in vector_results:
            item = hit["payload"]
            doc_id = item.get("doc_id")
            
            # Fetch connected documents/entities from the graph
            if doc_id:
                graph_query = """
                MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK|BELONGS_TO|CONTAINS|HAS_DOCUMENT|REPLIES_TO|BLOCKS*1..2]-(related)
                RETURN related.id AS id, labels(related) AS labels, related.title AS title
                LIMIT 5
                """
                try:
                    related = await self.graph_repo.execute_query(graph_query, {"doc_id": doc_id})
                    item["graph_context"] = related
                except Exception as e:
                    item["graph_context"] = []
                    print(f"Graph context error: {e}")
            
            expanded_results.append({
                "id": hit["id"],
                "score": hit["score"],
                "payload": item
            })
            
        return expanded_results
