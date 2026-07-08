import random

class SyntheticDataGenerator:
    def generate_tasks(self, count: int = 10) -> list:
        """
        Generates synthetic tasks to stress test the planner and agents.
        In production, this would use a fast LLM to generate diverse Edge Cases.
        """
        tasks = []
        templates = [
            "Write a python script to sort an array",
            "Research the latest features in PostgreSQL 16",
            "Summarize this legal document",
            "Generate a unit test for a FastAPI router"
        ]
        
        for _ in range(count):
            tasks.append({
                "prompt": random.choice(templates),
                "difficulty": random.choice(["easy", "medium", "hard"])
            })
            
        return tasks
