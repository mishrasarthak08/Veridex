import pytest
import os
from unittest.mock import patch, MagicMock

from app.knowledge.connectors.handshake import HandshakeConnector
from app.knowledge.storage.minio_store import MinioStorage
from app.knowledge.parsers.base import DocumentParser
from app.knowledge.chunking.handshake import HandshakeChunker
from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.knowledge.indexing.sparse_store import BM25SparseStore
from app.knowledge.graph.repository import GraphRepository
from app.knowledge.graph.service import GraphService
from app.knowledge.ingestion.pipeline import IngestionPipeline

@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("CI") != "true", reason="Integration tests require Docker services")
async def test_handshake_ingestion_pipeline():
    # 1. Initialize dependencies
    connector = HandshakeConnector(api_token="dummy_token")
    storage = MinioStorage()
    parser = DocumentParser() 
    chunker = HandshakeChunker()
    embedder = LiteLLMEmbedder(model_name="text-embedding-3-small")
    vector_store = QdrantVectorStore(collection_name="test_veridex_knowledge")
    sparse_store = BM25SparseStore()
    
    graph_repo = GraphRepository()
    graph_store = GraphService(repository=graph_repo)

    await vector_store.ensure_collection_exists()
    await storage.ensure_bucket_exists()

    # Mock the litellm embedder so we don't need a real API key during tests
    async def mock_embed_documents(texts):
        return [[0.1] * 1536 for _ in texts]
        
    embedder.embed_documents = mock_embed_documents

    # Mock connector auth and sync
    async def mock_authenticate():
        return True
    connector.authenticate = mock_authenticate

    async def mock_sync():
        yield {
            "id": 1234,
            "title": "Software Engineer",
            "employer": {"name": "Tech Corp"},
            "description": "Must know Python.\n\nGreat benefits.",
            "url": "https://handshake/jobs/1234",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z"
        }
    connector.sync = mock_sync

    import uuid
    project_id = f"test_project_{uuid.uuid4()}"
    
    # Mock normalize to inject our unique project_id
    original_normalize = connector.normalize
    async def mock_normalize(raw_doc):
        doc = await original_normalize(raw_doc)
        doc["project_id"] = project_id
        return doc
    connector.normalize = mock_normalize

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
    docs = await graph_store.get_documents_in_project(project_id)
    assert len(docs) > 0, f"No documents found in Neo4j for {project_id}"
    
    # Check that chunks were attached in the graph
    doc_id = docs[0]["document_id"]
    query = "MATCH (d:Document {id: $doc_id})-[:HAS_CHUNK]->(c:Chunk) RETURN count(c) as chunk_count"
    result = await graph_repo.execute_query(query, {"doc_id": doc_id})
    assert result[0]["chunk_count"] > 0, "No chunks attached to the document in Neo4j"

    # Verify Qdrant
    search_results = await vector_store.search(query_vector=[0.1] * 1536, limit=100)
    found = any(res["payload"]["metadata"]["document_id"] == doc_id for res in search_results)
    
    assert found, "Qdrant payload doesn't match document ID"

    # Cleanup Neo4j state for testing
    await graph_repo.execute_write("MATCH (d:Document {id: $doc_id}) DETACH DELETE d", {"doc_id": doc_id})
    await graph_store.close()
