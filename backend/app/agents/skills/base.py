from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSkill(ABC):
    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
