import asyncio
from typing import Dict, Any, List, Callable

class AgentBus:
    """
    In-memory pub/sub for agents to broadcast events.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}

    async def publish(self, event_type: str, payload: Any):
        if event_type in self.subscribers:
            for queue in self.subscribers[event_type]:
                await queue.put(payload)

    async def wait_for(self, event_type: str) -> Any:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        queue = asyncio.Queue()
        self.subscribers[event_type].append(queue)
        
        payload = await queue.get()
        self.subscribers[event_type].remove(queue)
        return payload
