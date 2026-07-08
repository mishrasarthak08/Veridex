from typing import List, Dict, Any
from app.agents.skills.base import BaseSkill

class BaseAgent:
    name: str
    role: str
    goal: str
    backstory: str
    skills: List[BaseSkill] = []

    def __init__(self):
        pass

    async def run(self, task: Dict[str, Any], context: str = "") -> str:
        """
        Executes a task given the context.
        In a real implementation, this interacts with the LLM router from Sprint 2,
        passing its skills as tools.
        """
        # Placeholder for LLM interaction
        return f"[{self.name}] Completed task: {task.get('description', '')}"
