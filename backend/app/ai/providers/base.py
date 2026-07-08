from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Optional

class BaseProvider(ABC):
    """
    Abstract Base Class for all LLM providers.
    Ensures every provider implements the same interface.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def generate(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        """Generate a complete response."""
        pass

    @abstractmethod
    async def stream(self, model: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream the response."""
        pass
        
    @abstractmethod
    def count_tokens(self, model: str, messages: List[Dict[str, Any]]) -> int:
        """Count tokens for the given input."""
        pass
