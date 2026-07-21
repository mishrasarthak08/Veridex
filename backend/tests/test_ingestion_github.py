import pytest
import os
from unittest.mock import patch, MagicMock

from app.knowledge.connectors.github import GitHubConnector
from app.knowledge.storage.minio_store import MinioStorage
from app.knowledge.parsers.base import DocumentParser
from app.knowledge.chunking.token import TokenChunker
from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.knowledge.indexing.sparse_store import BM25SparseStore
from app.knowledge.graph.repository import GraphRepository
from app.knowledge.graph.service import GraphService
from app.knowledge.ingestion.pipeline import IngestionPipeline

@pytest.mark.asyncio
async def test_github_ingestion_pipeline():
    # 1. Initialize dependencies
    connector = GitHubConnector(access_token="dummy", repository_full_name="test/repo")
    storage = MinioStorage()
    parser = DocumentParser() 
    chunker = TokenChunker(chunk_size=10, chunk_overlap=2)
    embedder = LiteLLMEmbedder(model_name="text-embedding-3-small")
    vector_store = QdrantVectorStore(collection_name="test_veridex_knowledge_github")
    sparse_store = BM25SparseStore()
    
    graph_repo = GraphRepository()
    graph_store = GraphService(repository=graph_repo)

    await vector_store.ensure_collection_exists()
    await storage.ensure_bucket_exists()

    # Mock embeddings
    async def mock_embed_documents(texts):
        return [[0.2] * 1536 for _ in texts]
    embedder.embed_documents = mock_embed_documents

    # Mock connector sync to avoid real GitHub API calls
    async def mock_sync():
        yield {
            "type": "issue",
            "source_id": "github:test/repo:issue:1",
            "content": "Bug in ingestion\n\nThe pipeline fails when ingesting.",
            "metadata": {
                "number": 1,
                "title": "Bug in ingestion",
                "url": "http://github.com/test/repo/issues/1",
                "state": "open",
                "author": "octocat"
            }
        }
    connector.sync = mock_sync

    # Mock authentication
    async def mock_authenticate():
        return True
    connector.authenticate = mock_authenticate

    # 2. Setup the pipeline
    pipeline = IngestionPipeline(
        connector=connector,
        storage=storage,
        parser=parser,
        chunker=chunker,
        embedder=embedder,
        vector_store=vector_store,
        sparse_store=sparse_store,
        graph_store=graph_store
    )

    # 3. Run the pipeline
    await pipeline.run()

    # 4. Verify outcomes
    # Verify Neo4j
    docs = await graph_store.get_documents_in_project("unassigned_project")
    assert len(docs) > 0, "No documents found in Neo4j for the unassigned project"
    
    # We should find the GitHub issue
    doc_id = "github:test/repo:issue:1"
    query = "MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk) RETURN count(c) as chunk_count"
    result = await graph_repo.execute_query(query, {"doc_id": doc_id})
    assert result[0]["chunk_count"] > 0, "No chunks attached to the GitHub document in Neo4j"

    # Verify Qdrant
    search_results = await vector_store.search(query_vector=[0.2] * 1536, limit=1)
    assert len(search_results) > 0, "No vectors found in Qdrant"
    assert search_results[0]["payload"]["metadata"]["document_id"] == doc_id, "Qdrant payload doesn't match GitHub document ID"

    # Cleanup Neo4j state for testing
    await graph_repo.execute_write("MATCH (d:Document {id: $doc_id}) DETACH DELETE d", {"doc_id": doc_id})
    await graph_store.close()
