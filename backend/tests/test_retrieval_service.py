import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock
from app.services.retrieval_service import RetrievalService

@pytest_asyncio.fixture
async def retrieval_service():
    # Mock the internal stores so we don't need real Qdrant/Redis running
    with patch('app.knowledge.embeddings.litellm_embedder.LiteLLMEmbedder'), \
         patch('app.knowledge.indexing.vector_store.QdrantVectorStore'), \
         patch('app.knowledge.indexing.sparse_store.BM25SparseStore'):
        service = RetrievalService()
        yield service

@pytest.mark.asyncio
async def test_tenant_isolation_in_retrieval(retrieval_service):
    """
    Ensure that the RetrievalService strictly passes tenant_id to the underlying retriever.
    """
    tenant_id = "tenant_A"
    
    with patch.object(retrieval_service.retriever, 'retrieve', new_callable=AsyncMock) as mock_retrieve:
        mock_retrieve.return_value = [{"id": "doc1", "content": "test"}]
        
        results = await retrieval_service.search("test query", tenant_id=tenant_id, limit=5)
        
        assert len(results) == 1
        mock_retrieve.assert_called_once_with("test query", limit=5, tenant_id=tenant_id)
