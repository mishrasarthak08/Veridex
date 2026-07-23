import pytest
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.knowledge.connectors.filesystem import FileSystemConnector
from app.knowledge.storage.minio_store import MinioStorage
from app.knowledge.parsers.base import DocumentParser
from app.knowledge.chunking.token import TokenChunker
from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.knowledge.indexing.sparse_store import BM25SparseStore
from app.knowledge.graph.repository import GraphRepository
from app.knowledge.graph.service import GraphService
from app.knowledge.ingestion.pipeline import IngestionPipeline

# We use the existing Docker infrastructure
# MinIO: 9000/9001
# Neo4j: 7687
# Qdrant: 6333

TEST_DIR = Path("/tmp/veridex_test_fs")

@pytest.fixture(autouse=True)
def setup_test_files():
    # Setup
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    TEST_DIR.mkdir(parents=True)
    
    test_file = TEST_DIR / "test_doc.txt"
    test_file.write_text("This is a test document. It contains some text that we want to chunk and embed. Veridex is an awesome AI agent orchestration platform.", encoding="utf-8")
    
    yield
    
    # Teardown
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)

@pytest.mark.asyncio
async def test_filesystem_ingestion_pipeline():
    # 1. Initialize dependencies
    connector = FileSystemConnector(root_dir=str(TEST_DIR))
    storage = MinioStorage()
    parser = DocumentParser() # Just passes text through for now
    chunker = TokenChunker(chunk_size=10, chunk_overlap=2)
    embedder = LiteLLMEmbedder(model_name="text-embedding-3-small")
    vector_store = QdrantVectorStore(collection_name="test_veridex_knowledge")
    sparse_store = BM25SparseStore()
    
    graph_repo = GraphRepository()
    graph_store = GraphService(repository=graph_repo)

    await vector_store.ensure_collection_exists()
    await storage.ensure_bucket_exists()

    # Mock the litellm embedder so we don't need a real API key during tests
    async def mock_embed_documents(texts):
        # Return a dummy vector of 1536 dimensions for each text
        return [[0.1] * 1536 for _ in texts]
        
    embedder.embed_documents = mock_embed_documents

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
    # Let's search with a dummy vector and filter by our specific document_id
    search_results = await vector_store.search(query_vector=[0.1] * 1536, limit=1)
    
    # Actually, the search might return an old document since they all have the same dummy vector.
    # We should just verify it exists by checking if any result matches, or filtering.
    # Since QdrantVectorStore doesn't expose a filter param in the mock test easily, we'll just 
    # check that it successfully inserted without asserting the exact document_id match if there are multiple.
    found = any(res["payload"]["metadata"]["document_id"] == doc_id for res in search_results)
    if not found:
        # fetch more just in case
        search_results = await vector_store.search(query_vector=[0.1] * 1536, limit=100)
        found = any(res["payload"]["metadata"]["document_id"] == doc_id for res in search_results)
    
    assert found, "Qdrant payload doesn't match document ID"

    # Cleanup Neo4j state for testing
    await graph_repo.execute_write("MATCH (d:Document {id: $doc_id}) DETACH DELETE d", {"doc_id": doc_id})
    await graph_store.close()
