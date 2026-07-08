from typing import Dict, Any, List
import asyncio

from ..connectors.base import BaseConnector
from ..storage.base import BaseStorage
from ..parsers.base import DocumentParser
from ..chunking.base import BaseChunker
from ..embeddings.base import BaseEmbedder
from ..indexing.vector_store import QdrantVectorStore
from ..indexing.sparse_store import BM25SparseStore
from ..graph.service import GraphService

class IngestionPipeline:
    def __init__(
        self,
        connector: BaseConnector,
        storage: BaseStorage,
        parser: DocumentParser,
        chunker: BaseChunker,
        embedder: BaseEmbedder,
        vector_store: QdrantVectorStore,
        sparse_store: BM25SparseStore,
        graph_store: GraphService
    ):
        self.connector = connector
        self.storage = storage
        self.parser = parser
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store
        self.sparse_store = sparse_store
        self.graph_store = graph_store

    async def run(self):
        """
        Executes the full ingestion lifecycle:
        Discovered -> Downloaded -> Normalized -> Parsed -> Chunked -> Embedded -> Indexed -> Verified
        """
        if not await self.connector.authenticate():
            raise Exception("Connector authentication failed")
            
        async for raw_doc in self.connector.sync():
            # 1. Normalize
            doc = await self.connector.normalize(raw_doc)
            
            # 2. Store raw backup (Downloaded)
            content_bytes = doc["content"].encode('utf-8')
            storage_path = await self.storage.upload(
                object_name=f"raw/{doc['id'].replace('/', '_')}", 
                data=content_bytes,
                content_type="text/plain"
            )
            doc["storage_path"] = storage_path
            
            # 3. Parse
            parsed_text = self.parser.parse(doc)
            
            # 4. Chunk
            chunks = self.chunker.chunk(parsed_text, metadata=doc["source_metadata"])
            
            if not chunks:
                continue
                
            chunk_texts = [c["text"] for c in chunks]
            
            # 5. Embed
            embeddings = await self.embedder.embed_documents(chunk_texts)
            
            # 6. Metadata Enrichment & Index (Dense + Sparse)
            import time
            enriched_chunks = []
            ids = []
            
            for idx, (c, ctext) in enumerate(zip(chunks, chunk_texts)):
                chunk_id = f"{doc['id']}_chunk_{idx}"
                ids.append(chunk_id)
                
                # Enterprise Metadata Injection
                enriched_metadata = {
                    **c.get("metadata", {}),
                    "tenant_id": doc.get("tenant_id", "default_tenant"),
                    "workspace_id": doc.get("workspace_id", "default_workspace"),
                    "document_id": doc["id"],
                    "chunk_id": chunk_id,
                    "source": doc.get("source", "unknown"),
                    "timestamp": int(time.time()),
                    "embedding_version": getattr(self.embedder, "model_name", "unknown"),
                    "chunk_strategy": getattr(self.chunker, "__class__", type(self.chunker)).__name__
                }
                c["metadata"] = enriched_metadata
                enriched_chunks.append(c)
                
            try:
                await self.vector_store.add_vectors(
                    vectors=embeddings,
                    payloads=enriched_chunks,
                    ids=ids
                )
                
                # If sparse store expects synchronous execution, we handle it here,
                # ideally sparse_store is also made async in the future
                self.sparse_store.add_documents([
                    {"id": cid, "text": ctext, "metadata": c["metadata"]} 
                    for cid, ctext, c in zip(ids, chunk_texts, enriched_chunks)
                ])
            except Exception as e:
                print(f"Failed to index chunks for document {doc['id']}: {e}")
                raise e # We want the task queue to retry this failure
            
            # 7. Graph (Relationships)
            # Ensure graph indexing fails gracefully without reverting MinIO and Qdrant success
            try:
                # We need a project ID to link to. Usually this comes from doc metadata.
                # If not provided, we link to a default "unassigned" project.
                project_id = doc.get("project_id", "unassigned_project")
                
                # Pass just the chunk IDs and metadata to Neo4j
                graph_chunks = [{"chunk_id": c["chunk_id"]} for c in enriched_chunks]
                
                await self.graph_store.ingest_document(
                    project_id=project_id,
                    doc_id=doc["id"],
                    title=doc.get("title", doc["id"]),
                    chunks=graph_chunks
                )
            except Exception as e:
                print(f"WARNING: Graph ingestion failed for document {doc['id']}: {e}")
                # We do NOT raise here. 
                # Qdrant and MinIO succeeded, so the document is fundamentally ingested.
                # A background synchronization task can fix graph discrepancies later.
            
            print(f"Successfully ingested {doc.get('title', doc['id'])} into Knowledge Platform")
