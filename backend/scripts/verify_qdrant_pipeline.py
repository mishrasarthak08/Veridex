import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.embeddings.openai_embedder import OpenAIEmbedder
from app.knowledge.indexing.vector_store import QdrantVectorStore
from app.core.config import settings

async def main():
    if not settings.OPENAI_API_KEY:
        print("ERROR: Please set OPENAI_API_KEY in your .env file before running.")
        sys.exit(1)
        
    print("1. Initializing components...")
    embedder = OpenAIEmbedder()
    vector_store = QdrantVectorStore()
    
    print("2. Ensuring Qdrant collection exists...")
    await vector_store.ensure_collection_exists()
    
    print("3. Generating embeddings using text-embedding-3-small...")
    texts = [
        "Veridex is a multi-tenant agent orchestration platform designed for enterprise reliability.",
        "Qdrant provides scalable hybrid vector search capabilities."
    ]
    embeddings = await embedder.embed_documents(texts)
    print(f"   -> Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}.")
    
    print("4. Upserting vectors to Qdrant with enterprise metadata...")
    payloads = [
        {"text": texts[0], "metadata": {"tenant_id": "tenant_1", "source": "docs"}},
        {"text": texts[1], "metadata": {"tenant_id": "tenant_2", "source": "docs"}}
    ]
    await vector_store.add_vectors(embeddings, payloads)
    print("   -> Upsert complete.")
    
    # Slight delay to ensure indexing
    await asyncio.sleep(1)
    
    print("5. Performing metadata-filtered vector search (tenant_id = tenant_1)...")
    query = "What is Veridex?"
    query_vector = await embedder.embed_query(query)
    
    # Exact match filter
    results = await vector_store.search(
        query_vector=query_vector,
        limit=2,
        metadata_filters={"metadata.tenant_id": "tenant_1"}
    )
    
    print(f"\nResults ({len(results)} found):")
    for r in results:
        print(f" - Score: {r['score']:.4f}")
        print(f"   Text:  {r['payload']['text']}")
        print(f"   Tenant: {r['payload']['metadata']['tenant_id']}")
        
    if len(results) == 1 and results[0]['payload']['metadata']['tenant_id'] == 'tenant_1':
        print("\nSUCCESS: The pipeline successfully embedded, stored, and filtered the documents based on tenant isolation.")
    else:
        print("\nFAILED: Isolation or search did not return expected results.")

if __name__ == "__main__":
    asyncio.run(main())
