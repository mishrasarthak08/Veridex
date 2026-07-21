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

class PlanningEngine:
    async def decompose(self, goal: str) -> List[TaskNode]:
        """
        For Phase 1, we use a fixed single-step execution strategy.
        This de-risks the queue plumbing separately from LLM planning logic.
        """
        execution_task = TaskNode(
            description=goal, 
            agent_role="Executor"
        )
        return [execution_task]
