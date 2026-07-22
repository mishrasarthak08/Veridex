import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.knowledge.graph.repository import GraphRepository

async def seed_graph():
    print("Connecting to Neo4j to seed dummy data...")
    repo = GraphRepository()
    
    # Clean existing
    await repo.execute_write("MATCH (n) DETACH DELETE n")
    
    # Create nodes and relationships
    query = """
    CREATE (p1:Person {id: 'p1', name: 'Alice', role: 'Engineer'})
    CREATE (p2:Person {id: 'p2', name: 'Bob', role: 'Manager'})
    CREATE (p3:Person {id: 'p3', name: 'Charlie', role: 'Data Scientist'})
    
    CREATE (o1:Organization {id: 'o1', name: 'Veridex'})
    CREATE (o2:Organization {id: 'o2', name: 'Acme Corp'})
    
    CREATE (d1:Document {id: 'd1', title: 'Veridex Architecture'})
    CREATE (d2:Document {id: 'd2', title: 'Q3 Financials'})
    
    CREATE (p1)-[:WORKS_FOR]->(o1)
    CREATE (p2)-[:WORKS_FOR]->(o1)
    CREATE (p3)-[:WORKS_FOR]->(o2)
    
    CREATE (p1)-[:AUTHORED]->(d1)
    CREATE (p2)-[:REVIEWED]->(d1)
    
    CREATE (o2)-[:OWNS]->(d2)
    """
    await repo.execute_write(query)
    
    print("Seeding complete! Dummy graph data injected.")
    await repo.close()

if __name__ == "__main__":
    asyncio.run(seed_graph())
