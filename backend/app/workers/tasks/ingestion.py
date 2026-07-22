import asyncio
from celery import shared_task
from typing import Dict, Any

# We assume standard setup where dependencies are fetched asynchronously inside the task or via a dependency injector
@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_ingestion_job(self, document_id: str, doc_type: str, raw_text: str, metadata: Dict[str, Any]):
    """
    Background job to process raw documents:
    1. Chunk the document using the correct strategy
    2. Extract entities and relationships
    3. Generate embeddings
    4. Store chunks in vector DB
    5. Store graph structure in Neo4j
    """
    
    # We use a helper async runner for Celery since the internal tools are async
    def _run_async(coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    try:
        from app.knowledge.chunking.factory import ChunkerFactory
        from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
        from app.knowledge.storage.qdrant_store import QdrantStore
        from app.knowledge.graph.repository import GraphRepository
        from app.knowledge.graph.service import GraphService
        from app.knowledge.graph.extraction import GraphExtractor

        print(f"Starting ingestion for document {document_id} of type {doc_type}")
        
        # 1. Chunking
        chunker = ChunkerFactory.get_chunker(doc_type=doc_type)
        chunks = chunker.chunk(raw_text, metadata={"doc_id": document_id, **metadata})
        
        texts_to_embed = [c["text"] for c in chunks]
        chunk_metadatas = [c["metadata"] for c in chunks]
        
        if not texts_to_embed:
            print("No chunks generated. Skipping ingestion.")
            return

        # 2. Extract Entities
        extractor = GraphExtractor()
        # For cost/speed, maybe only extract from the top-level document or first few chunks, but here we process raw_text
        # In a real heavy system we'd extract entities chunk-by-chunk or from summaries
        entities = _run_async(extractor.extract_entities(raw_text[:8000])) # Limit to ~8k chars for LLM context

        # 3. Embedding
        embedder = LiteLLMEmbedder()
        embeddings = _run_async(embedder.embed_documents(texts_to_embed))

        # 4. Storage (Vector)
        vector_store = QdrantStore()
        _run_async(vector_store.upsert(texts=texts_to_embed, embeddings=embeddings, metadata=chunk_metadatas))

        # 5. Storage (Graph)
        repo = GraphRepository()
        service = GraphService(repo)
        
        # We assume a generic 'ingest_document' is enough for basic ingestion if not specific
        _run_async(service.ingest_document(
            project_id=metadata.get("project_id", "default_project"),
            doc_id=document_id,
            title=metadata.get("title", f"Document {document_id}"),
            chunks=[{"chunk_id": f"{document_id}_{i}"} for i in range(len(chunks))]
        ))
        _run_async(service.close())
        
        print(f"Ingestion complete for document {document_id}")

    except Exception as exc:
        print(f"Error processing ingestion job: {exc}")
        self.retry(exc=exc)
