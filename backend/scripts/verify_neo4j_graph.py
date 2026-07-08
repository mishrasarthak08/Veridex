import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.knowledge.graph.repository import GraphRepository
from app.knowledge.graph.service import GraphService
from neo4j.exceptions import ServiceUnavailable

async def main():
    print("1. Initializing Neo4j GraphService...")
    repo = GraphRepository()
    service = GraphService(repo)
    
    org_id = "org_1"
    workspace_id = "ws_1"
    project_id = "proj_1"
    doc_id = "doc_1"
    
    try:
        print("2. Testing connection and resetting state...")
        # Just a simple query to ensure we can connect
        await repo.execute_query("RETURN 1 as test")
        
        # Clean up test nodes to avoid duplicates across test runs
        await repo.execute_write("MATCH (n) WHERE n.id IN [$org_id, $ws_id, $proj_id, $doc_id] DETACH DELETE n", 
                                 {"org_id": org_id, "ws_id": workspace_id, "proj_id": project_id, "doc_id": doc_id})
        
        print("3. Building Graph Hierarchy (Org -> Workspace -> Project)...")
        await service.create_organization_workspace_link(org_id, workspace_id, "Veridex Corp", "Engineering")
        await service.create_workspace_project_link(workspace_id, project_id, "Platform V2")
        
        print("4. Simulating Document Ingestion...")
        chunks = [{"chunk_id": "chunk_1"}, {"chunk_id": "chunk_2"}]
        await service.ingest_document(project_id, doc_id, "Neo4j Architecture Design", chunks)
        
        print("5. Running Verification Queries...")
        
        print("   -> Querying projects in workspace...")
        projects = await service.get_projects_in_workspace(workspace_id)
        print(f"      Result: {[p['name'] for p in projects]}")
        assert len(projects) == 1
        
        print("   -> Querying documents in project...")
        docs = await service.get_documents_in_project(project_id)
        print(f"      Result: {[d['title'] for d in docs]}")
        assert len(docs) == 1
        assert docs[0]['document_id'] == doc_id
        
        print("\nSUCCESS: Neo4j relationship engine is fully operational!")
        
    except ServiceUnavailable:
        print("\nFAILED: Could not connect to Neo4j. Is the docker container running?")
    except AssertionError:
        print("\nFAILED: Graph query results did not match expectations.")
    except Exception as e:
        print(f"\nFAILED: Unexpected error: {e}")
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(main())
