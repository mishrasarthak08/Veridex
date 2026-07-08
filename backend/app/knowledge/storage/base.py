from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    async def upload(self, object_name: str, data: bytes, content_type: str) -> str:
        pass
        
    @abstractmethod
    async def download(self, object_name: str) -> bytes:
        pass
