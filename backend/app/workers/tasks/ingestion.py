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
    
    def _run_async(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
            
        if loop and loop.is_running():
            return loop.create_task(coro)
        else:
            return asyncio.run(coro)

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

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_connector_job(self, connector_type: str, config: Dict[str, Any]):
    """
    Background job to run a full ingestion pipeline for a given connector.
    """
    def _run_async(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
            
        if loop and loop.is_running():
            return loop.create_task(coro)
        else:
            return asyncio.run(coro)
        
    try:
        from app.knowledge.connectors.filesystem import FileSystemConnector
        from app.knowledge.connectors.github import GitHubConnector
        from app.knowledge.storage.minio_store import MinioStorage
        from app.knowledge.parsers.base import DocumentParser
        from app.knowledge.chunking.recursive import RecursiveCharacterChunker
        from app.knowledge.embeddings.litellm_embedder import LiteLLMEmbedder
        from app.knowledge.indexing.vector_store import QdrantVectorStore
        from app.knowledge.indexing.sparse_store import BM25SparseStore
        from app.knowledge.graph.service import GraphService
        from app.knowledge.graph.repository import GraphRepository
        from app.knowledge.ingestion.pipeline import IngestionPipeline

        print(f"Starting sync job for connector: {connector_type} with config: {config}")

        from app.core.config import settings

        if connector_type == "filesystem":
            connector = FileSystemConnector(root_dir=config.get("directory_path", "./"))
        elif connector_type == "github":
            connector = GitHubConnector(
                access_token=config.get("access_token") or settings.GITHUB_TOKEN,
                repository_full_name=config.get("repository_full_name", "")
            )
        elif connector_type == "slack":
            from app.knowledge.connectors.slack import SlackConnector
            connector = SlackConnector(
                bot_token=config.get("bot_token") or settings.SLACK_BOT_TOKEN
            )
        else:
            raise ValueError(f"Unsupported connector type: {connector_type}")

        # Instantiate components
        storage = MinioStorage()
        parser = DocumentParser()
        chunker = RecursiveCharacterChunker()
        embedder = LiteLLMEmbedder()
        vector_store = QdrantVectorStore()
        _run_async(vector_store.ensure_collection_exists())
        sparse_store = BM25SparseStore()
        
        repo = GraphRepository()
        graph_store = GraphService(repo)

        pipeline = IngestionPipeline(
            connector, storage, parser, chunker, embedder, vector_store, sparse_store, graph_store
        )
        
        # Execute the pipeline
        _run_async(pipeline.run())
        
        # Cleanup
        _run_async(repo.close())

        print(f"Sync job complete for connector: {connector_type}")

    except Exception as exc:
        print(f"Error processing sync_connector_job: {exc}")
        self.retry(exc=exc)
