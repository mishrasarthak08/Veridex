from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseConnector(ABC):
    name: str

    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def sync(self) -> List[Dict[str, Any]]:
        """
        Polls the source for data. 
        Returns a list of raw objects.
        """
        pass

    @abstractmethod
    async def normalize(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a raw object into a standard Veridex Document or Event.
        """
        pass

    @abstractmethod
    async def watch(self):
        """
        Starts listening for realtime events if polling isn't used.
        """
        pass
