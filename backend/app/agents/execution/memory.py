from typing import Dict, Any, List

class WorkspaceMemory:
    """
    A shared collaborative memory for agents working on the same goal.
    This replaces isolated agent short-term memory.
    """
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        self.facts: List[str] = []
        self.scratchpad: Dict[str, Any] = {}
        
    def add_fact(self, fact: str):
        self.facts.append(fact)
        
    def get_context(self) -> str:
        return "\n".join([f"- {fact}" for fact in self.facts])
        
    def set_var(self, key: str, value: Any):
        self.scratchpad[key] = value
        
    def get_var(self, key: str) -> Any:
        return self.scratchpad.get(key)
