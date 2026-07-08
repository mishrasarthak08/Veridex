from typing import Dict, Any, List
import uuid

class TaskNode:
    def __init__(self, description: str, agent_role: str, dependencies: List[str] = None):
        self.id = str(uuid.uuid4())
        self.description = description
        self.agent_role = agent_role
        self.dependencies = dependencies or []

class PlanningEngine:
    async def decompose(self, goal: str) -> List[TaskNode]:
        """
        In a real scenario, this asks an LLM (like GPT-4o or Claude 3.5 Sonnet) 
        to break down the goal into a DAG of TaskNodes.
        For now, we simulate a hardcoded DAG.
        """
        # Simulated DAG
        research_task = TaskNode(
            description=f"Research context for: {goal}", 
            agent_role="Researcher"
        )
        write_task = TaskNode(
            description="Write a summary report based on research", 
            agent_role="Writer",
            dependencies=[research_task.id]
        )
        review_task = TaskNode(
            description="Review the report for quality and accuracy", 
            agent_role="Critic",
            dependencies=[write_task.id]
        )
        return [research_task, write_task, review_task]
