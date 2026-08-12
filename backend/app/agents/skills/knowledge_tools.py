from app.agents.registry.tools import tool
from app.knowledge.retrieval.hybrid import HybridRetriever
from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.knowledge.indexing.sparse_store import BM25SparseStore
import json
from app.knowledge.graph.cypher_generator import CypherGenerator

@tool
async def query_knowledge_graph(query: str, tenant_id: str) -> str:
    """
    Translates a natural language query into a Graph Database (Neo4j) Cypher query,
    executes it, and returns the structural or relational results.
    Use this tool when answering questions about relationships (e.g. who works where, who authored what).
    """
    try:
        generator = CypherGenerator()
        return await generator.generate_and_run(query, tenant_id)
    except Exception as e:
        return f"Error querying knowledge graph: {e}"

@tool
async def search_knowledge(query: str, limit: int = 5) -> str:
    """
    Searches the internal knowledge base for relevant context regarding the query.
    Use this to find company policies, documentation, and specific internal facts.
    """
    try:
        embedder = LiteLLMEmbedder()
        vector_store = QdrantVectorStore()
        sparse_store = BM25SparseStore()
        
        retriever = HybridRetriever(embedder, vector_store, sparse_store)
        results = await retriever.retrieve(query, limit=limit)
        
        if not results:
            return "No relevant information found in the knowledge base."
            
        # Format results nicely for the LLM
        formatted_results = []
        for i, res in enumerate(results):
            content = res.get("content", "")
            score = res.get("score", 0)
            formatted_results.append(f"Result {i+1} (Score: {score:.2f}):\n{content}")
            
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"Error searching knowledge base: {e}"
