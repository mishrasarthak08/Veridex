from typing import Dict, Any, List
import uuid

class TaskNode:
    def __init__(self, description: str, agent_role: str, dependencies: List[str] = None, id: str = None):
        self.id = id if id else str(uuid.uuid4())
        self.description = description
        self.agent_role = agent_role
        self.dependencies = dependencies or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "agent_role": self.agent_role,
            "dependencies": self.dependencies,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskNode":
        return cls(
            id=data.get("id"),
            description=data.get("description"),
            agent_role=data.get("agent_role"),
            dependencies=data.get("dependencies", [])
        )

import json
from litellm import acompletion
from app.core.config import settings

class PlanningEngine:
    def __init__(self, model_name: str = "gemini/gemini-2.5-flash"):
        self.model_name = model_name

    async def decompose(self, goal: str) -> List[TaskNode]:
        """
        Uses an LLM to decompose a high-level goal into a Directed Acyclic Graph (DAG) of subtasks.
        """
        prompt = f"""
You are an expert Planner Agent. Your job is to decompose the following complex goal into a logical sequence of subtasks (a Directed Acyclic Graph).
Each subtask must be independent and executable by a single agent worker using tools.

Goal: "{goal}"

Output a JSON object with a single key "tasks", which is an array of objects.
Each object must have:
- "id": A short, unique string identifier (e.g. "task_1", "fetch_data", "analyze")
- "description": A clear, actionable description of the subtask
- "agent_role": The role of the agent best suited for this task (e.g. "Executor", "Researcher")
- "dependencies": An array of "id" strings representing tasks that MUST complete before this task can start (empty array if no dependencies).

Output ONLY the JSON and nothing else.
"""
        try:
            response = await acompletion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting around JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            parsed = json.loads(content.strip())
            
            tasks = []
            for t in parsed.get("tasks", []):
                tasks.append(
                    TaskNode(
                        id=t.get("id"),
                        description=t.get("description"),
                        agent_role=t.get("agent_role", "Executor"),
                        dependencies=t.get("dependencies", [])
                    )
                )
            
            # Fallback to single task if the LLM didn't return any
            if not tasks:
                raise ValueError("No tasks parsed from LLM")
                
            return tasks
            
        except Exception as e:
            print(f"[Planner] Failed to decompose goal using LLM: {e}. Falling back to single execution.")
            return [TaskNode(description=goal, agent_role="Executor")]
