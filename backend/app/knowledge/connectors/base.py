from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator

class BaseConnector(ABC):
    """
    Abstract Base Class for Knowledge Connectors.
    """
    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def sync(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Full sync: Yields raw document blobs and metadata."""
        pass

    @abstractmethod
    async def incremental_sync(self, last_sync: str) -> AsyncGenerator[Dict[str, Any], None]:
        pass

    @abstractmethod
    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert connector-specific metadata to a standard format."""
        pass
