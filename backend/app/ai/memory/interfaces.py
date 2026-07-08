from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseMemory(ABC):
    @abstractmethod
    async def add(self, role: str, content: str, **kwargs):
        pass

    @abstractmethod
    async def get_all(self) -> List[Dict[str, Any]]:
        pass

class ShortTermMemory(BaseMemory):
    """In-memory list of messages for a single conversation/task."""
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    async def add(self, role: str, content: str, **kwargs):
        msg = {"role": role, "content": content}
        if kwargs:
            msg.update(kwargs)
        self.messages.append(msg)

    async def get_all(self) -> List[Dict[str, Any]]:
        return self.messages

class SemanticMemory(ABC):
    """Vector-backed memory (Placeholder for Sprint 3)."""
    pass

class LongTermMemory(ABC):
    """Postgres-backed memory for user/workspace facts."""
    pass
