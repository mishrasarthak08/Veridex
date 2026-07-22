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

from app.workers.tasks.ingestion import sync_connector_job

class SyncRequest(BaseModel):
    connector_type: str
    config: Dict[str, Any]

class RetrieveRequest(BaseModel):
    query: str
    limit: int = 5

@router.post("/sync")
async def trigger_sync(request: SyncRequest):
    # Dispatch to Celery using apply_async
    task = sync_connector_job.apply_async(
        args=[request.connector_type, request.config]
    )
    return {"status": "Sync triggered successfully", "task_id": task.id}

@router.post("/retrieve")
async def retrieve_knowledge(request: RetrieveRequest):
    retriever = HybridRetriever(embedder, vector_store, sparse_store)
    results = await retriever.retrieve(request.query, limit=request.limit)
    return {"query": request.query, "results": results}

@router.get("/graph")
async def get_graph_data():
    """
    Fetches the Knowledge Graph structure (nodes and edges) for UI visualization.
    """
    query = """
    MATCH (n)
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    repo = GraphRepository()
    records = await repo.execute_query(query)
    
    nodes = {}
    edges = []
    
    for record in records:
        n = record["n"]
        if n:
            n_id = n.get("id") or str(n.element_id)
            nodes[n_id] = {
                "id": n_id,
                "label": list(n.labels)[0] if n.labels else "Unknown",
                "properties": dict(n)
            }
            
        r = record["r"]
        m = record["m"]
        if r and m:
            m_id = m.get("id") or str(m.element_id)
            nodes[m_id] = {
                "id": m_id,
                "label": list(m.labels)[0] if m.labels else "Unknown",
                "properties": dict(m)
            }
            edges.append({
                "source": n_id,
                "target": m_id,
                "type": r.type
            })
            
    await repo.close()
    
    return {
        "nodes": list(nodes.values()),
        "edges": edges
    }

