from abc import ABC, abstractmethod
from typing import Dict, Any, Type
from pydantic import BaseModel

class BaseTool(ABC):
    """
    Abstract Base Class for all AI Tools.
    Enforces a strict interface for tools to be registered and executed safely.
    """
    name: str
    description: str
    schema: Type[BaseModel]

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
