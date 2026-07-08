from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConnector(ABC):
    @abstractmethod
    def sync(self) -> Dict[str, Any]:
        """Synchronizes data from the external source."""
        pass

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
