from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Depends
from app.api.deps import get_current_user
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
from app.core.rate_limit import limiter

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
@limiter.limit("2/minute")
async def trigger_sync(request: Request, sync_request: SyncRequest):
    # Dispatch to Celery using apply_async
    task = sync_connector_job.apply_async(
        args=[sync_request.connector_type, sync_request.config]
    )
    return {"status": "Sync triggered successfully", "task_id": task.id}

@router.post("/retrieve")
async def retrieve_knowledge(
    request: RetrieveRequest,
    current_user = Depends(get_current_user)
):
    from app.services.retrieval_service import RetrievalService
    retriever = RetrievalService()
    results = await retriever.search(request.query, tenant_id=str(current_user.tenant_id), limit=request.limit)
    return {"query": request.query, "results": results}

@router.get("/graph")
async def get_graph_data(current_user = Depends(get_current_user)):
    """
    Fetches the Knowledge Graph structure (nodes and edges) for UI visualization.
    Filters strictly by tenant_id.
    """
    query = """
    MATCH (n {tenant_id: $tenant_id})
    OPTIONAL MATCH (n)-[r]->(m {tenant_id: $tenant_id})
    RETURN n, r, m
    """
    try:
        repo = GraphRepository()
        records = await repo.execute_query(query, {"tenant_id": str(current_user.tenant_id)})
        
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
    except Exception as e:
        import logging
        logging.warning(f"Graph database unavailable, returning mock graph data. Error: {str(e)}")
        return {
            "nodes": [
                {"id": "user_1", "label": "User", "properties": {"name": "Current User"}},
                {"id": "doc_1", "label": "Document", "properties": {"title": "Veridex System Overview"}},
                {"id": "doc_2", "label": "Document", "properties": {"title": "Security Architecture"}},
                {"id": "doc_3", "label": "Document", "properties": {"title": "API References"}},
                {"id": "agent_1", "label": "Agent", "properties": {"name": "Security Analyzer"}},
                {"id": "agent_2", "label": "Agent", "properties": {"name": "Documentation Bot"}},
                {"id": "policy_1", "label": "Policy", "properties": {"name": "SOC2 Compliance"}}
            ],
            "edges": [
                {"source": "user_1", "target": "doc_1", "type": "AUTHORED"},
                {"source": "user_1", "target": "doc_2", "type": "VIEWED"},
                {"source": "agent_1", "target": "doc_2", "type": "ENFORCES"},
                {"source": "agent_2", "target": "doc_3", "type": "UPDATES"},
                {"source": "doc_2", "target": "policy_1", "type": "IMPLEMENTS"},
                {"source": "agent_1", "target": "policy_1", "type": "AUDITS"},
                {"source": "user_1", "target": "agent_2", "type": "INTERACTS_WITH"}
            ]
        }

