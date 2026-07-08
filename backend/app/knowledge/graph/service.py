from typing import List, Dict, Any
from .repository import GraphRepository

class GraphService:
    def __init__(self, repository: GraphRepository):
        self.repo = repository
        
    async def close(self):
        await self.repo.close()

    # ==================
    # MUTATIONS
    # ==================
    async def create_organization_workspace_link(self, org_id: str, workspace_id: str, org_name: str = "", workspace_name: str = ""):
        query = """
        MERGE (o:Organization {id: $org_id})
        ON CREATE SET o.name = $org_name
        MERGE (w:Workspace {id: $workspace_id})
        ON CREATE SET w.name = $workspace_name
        MERGE (o)-[:OWNS]->(w)
        """
        await self.repo.execute_write(query, {"org_id": org_id, "workspace_id": workspace_id, "org_name": org_name, "workspace_name": workspace_name})

    async def create_workspace_project_link(self, workspace_id: str, project_id: str, project_name: str = ""):
        query = """
        MERGE (w:Workspace {id: $workspace_id})
        MERGE (p:Project {id: $project_id})
        ON CREATE SET p.name = $project_name
        MERGE (w)-[:CONTAINS]->(p)
        """
        await self.repo.execute_write(query, {"workspace_id": workspace_id, "project_id": project_id, "project_name": project_name})

    async def ingest_document(self, project_id: str, doc_id: str, title: str, chunks: List[Dict[str, Any]]):
        """
        Links a document to a project, and links all its chunks to the document.
        """
        query = """
        MERGE (p:Project {id: $project_id})
        MERGE (d:Document {id: $doc_id})
        SET d.title = $title
        MERGE (p)-[:HAS_DOCUMENT]->(d)
        
        WITH d
        UNWIND $chunks as chunk
        MERGE (c:Chunk {id: chunk.chunk_id})
        MERGE (d)-[:HAS_CHUNK]->(c)
        """
        await self.repo.execute_write(query, {
            "project_id": project_id, 
            "doc_id": doc_id, 
            "title": title, 
            "chunks": chunks
        })

    async def record_agent_workflow(self, agent_id: str, workflow_id: str, tool_ids: List[str]):
        query = """
        MERGE (a:Agent {id: $agent_id})
        MERGE (w:Workflow {id: $workflow_id})
        MERGE (a)-[:EXECUTED]->(w)
        
        WITH w
        UNWIND $tool_ids as t_id
        MERGE (t:Tool {id: t_id})
        MERGE (w)-[:USED_TOOL]->(t)
        """
        await self.repo.execute_write(query, {
            "agent_id": agent_id,
            "workflow_id": workflow_id,
            "tool_ids": tool_ids
        })

    async def ingest_email(self, user_id: str, doc_id: str, thread_id: str, title: str, chunks: List[Dict[str, Any]]):
        """
        Links a User to an Email (SENT or RECEIVED depending on context, we'll just use SENT/RECEIVED logic or HAS_EMAIL for simplicity).
        Links an Email to a Thread.
        Links chunks to the Email document.
        """
        query = """
        MERGE (u:User {id: $user_id})
        MERGE (t:Thread {id: $thread_id})
        MERGE (d:Document {id: $doc_id})
        SET d.title = $title, d.type = 'email'
        
        MERGE (u)-[:HAS_EMAIL]->(d)
        MERGE (d)-[:BELONGS_TO]->(t)
        
        WITH d
        UNWIND $chunks as chunk
        MERGE (c:Chunk {id: chunk.chunk_id})
        MERGE (d)-[:HAS_CHUNK]->(c)
        """
        await self.repo.execute_write(query, {
            "user_id": user_id, 
            "doc_id": doc_id, 
            "thread_id": thread_id,
            "title": title, 
            "chunks": chunks
        })

    # ==================
    # QUERIES
    # ==================
    async def get_documents_in_project(self, project_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (p:Project {id: $project_id})-[:HAS_DOCUMENT]->(d:Document)
        RETURN d.id AS document_id, d.title AS title
        """
        return await self.repo.execute_query(query, {"project_id": project_id})

    async def get_workflows_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (a:Agent {id: $agent_id})-[:EXECUTED]->(w:Workflow)
        RETURN w.id AS workflow_id
        """
        return await self.repo.execute_query(query, {"agent_id": agent_id})
        
    async def get_projects_in_workspace(self, workspace_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (w:Workspace {id: $workspace_id})-[:CONTAINS]->(p:Project)
        RETURN p.id AS project_id, p.name AS name
        """
        return await self.repo.execute_query(query, {"workspace_id": workspace_id})
        
    async def get_tools_in_workflow(self, workflow_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (w:Workflow {id: $workflow_id})-[:USED_TOOL]->(t:Tool)
        RETURN t.id AS tool_id
        """
        return await self.repo.execute_query(query, {"workflow_id": workflow_id})
        
    async def get_connected_documents(self, doc_id: str) -> List[Dict[str, Any]]:
        # Find documents that share the same project
        query = """
        MATCH (d1:Document {id: $doc_id})<-[:HAS_DOCUMENT]-(p:Project)-[:HAS_DOCUMENT]->(d2:Document)
        WHERE d1.id <> d2.id
        RETURN d2.id AS document_id, d2.title AS title, p.id AS project_id
        """
        return await self.repo.execute_query(query, {"doc_id": doc_id})
