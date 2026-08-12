import json
from litellm import acompletion
from app.knowledge.graph.repository import GraphRepository

class CypherGenerator:
    """
    Generates Neo4j Cypher queries from natural language using an LLM.
    """
    def __init__(self, model_name: str = "gemini/gemini-2.5-flash"):
        self.model_name = model_name
        self.repo = GraphRepository()
        
        # In a real app, you would fetch this dynamically from the DB via `CALL db.schema.visualization()`
        self.schema = """
        Nodes:
        - Person {id: String, name: String, role: String, tenant_id: String}
        - Organization {id: String, name: String, tenant_id: String}
        - Document {id: String, title: String, tenant_id: String}
        
        Relationships:
        - (Person)-[:WORKS_FOR]->(Organization)
        - (Person)-[:AUTHORED]->(Document)
        - (Person)-[:REVIEWED]->(Document)
        - (Organization)-[:OWNS]->(Document)
        """

    async def generate_and_run(self, query: str, tenant_id: str) -> str:
        """
        Translates the query to Cypher, executes it with tenant isolation, and returns the result.
        """
        prompt = f"""
You are an expert Neo4j Cypher developer.
Convert the following natural language query into a Cypher query based on the schema provided.

Schema:
{self.schema}

Important Rules:
1. Every node pattern MUST include the tenant_id parameter for security: e.g., (p:Person {{tenant_id: $tenant_id}})
2. Do not use ANY nodes or relationships that are not defined in the schema.
3. Your output MUST be ONLY a valid JSON object with a single key "cypher" containing the query string. Do not include markdown formatting or explanation.

Natural Language Query: "{query}"
"""
        try:
            response = await acompletion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
                
            parsed = json.loads(content.strip())
            cypher_query = parsed.get("cypher")
            
            if not cypher_query:
                return "Error: LLM did not return a cypher query."
                
            # Execute the query
            records = await self.repo.execute_query(cypher_query, {"tenant_id": tenant_id})
            
            if not records:
                return f"The query '{cypher_query}' returned no results for this tenant."
                
            # Stringify the records for the agent
            result_str = "\n".join([str(record) for record in records])
            return f"Query executed: {cypher_query}\nResults:\n{result_str}"
            
        except Exception as e:
            return f"Failed to generate or execute Cypher query: {e}"
