from neo4j import AsyncGraphDatabase
from typing import Dict, Any, List

class Neo4jKnowledgeGraph:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="veridex_secret"):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        await self.driver.close()

    async def add_document_entity(self, doc_id: str, title: str):
        query = """
        MERGE (d:Document {id: $doc_id})
        SET d.title = $title
        """
        async with self.driver.session() as session:
            await session.run(query, doc_id=doc_id, title=title)

    async def link_document_to_project(self, doc_id: str, project_id: str):
        query = """
        MATCH (d:Document {id: $doc_id})
        MERGE (p:Project {id: $project_id})
        MERGE (p)-[:CONTAINS]->(d)
        """
        async with self.driver.session() as session:
            await session.run(query, doc_id=doc_id, project_id=project_id)
            
    async def get_document_context(self, doc_id: str) -> List[Dict[str, Any]]:
        query = """
        MATCH (d:Document {id: $doc_id})<-[:CONTAINS]-(p:Project)
        RETURN p.id AS project_id
        """
        async with self.driver.session() as session:
            result = await session.run(query, doc_id=doc_id)
            records = await result.data()
            return records
