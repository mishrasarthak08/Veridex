from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any

from app.knowledge.connectors.filesystem import FileSystemConnector
from app.knowledge.storage.minio_store import MinioStorage
from app.knowledge.parsers.base import DocumentParser
from app.knowledge.chunking.recursive import RecursiveCharacterChunker
from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.knowledge.indexing.sparse_store import BM25SparseStore
from app.knowledge.graph.service import GraphService
from app.knowledge.graph.repository import GraphRepository
from app.knowledge.ingestion.pipeline import IngestionPipeline
from app.knowledge.retrieval.hybrid import HybridRetriever

router = APIRouter()

# Global instances (in a real app, manage these properly with dependencies)
storage = MinioStorage()
parser = DocumentParser()
chunker = RecursiveCharacterChunker()
embedder = LiteLLMEmbedder()
vector_store = QdrantVectorStore()
sparse_store = BM25SparseStore()
graph_store = GraphService(GraphRepository())

class SyncRequest(BaseModel):
    directory_path: str

class RetrieveRequest(BaseModel):
    query: str
    limit: int = 5

@router.post("/sync")
async def trigger_sync(request: SyncRequest, background_tasks: BackgroundTasks):
    connector = FileSystemConnector(root_dir=request.directory_path)
    pipeline = IngestionPipeline(
        connector, storage, parser, chunker, embedder, vector_store, sparse_store, graph_store
    )
    # Run async in background
    background_tasks.add_task(pipeline.run)
    return {"status": "Sync triggered successfully"}

@router.post("/retrieve")
async def retrieve_knowledge(request: RetrieveRequest):
    retriever = HybridRetriever(embedder, vector_store, sparse_store)
    results = await retriever.retrieve(request.query, limit=request.limit)
    return {"query": request.query, "results": results}
