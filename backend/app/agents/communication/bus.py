import asyncio
from typing import Dict, Any, List
import json
import redis.asyncio as aioredis
from app.core.config import settings

class AgentBus:
    """
    Redis Pub/Sub for agents to broadcast events across workers.
    """
    def __init__(self):
        redis_url = f"redis://{settings.REDIS_SERVER}:{settings.REDIS_PORT}/0"
        self.redis = aioredis.from_url(redis_url)

    async def publish(self, event_type: str, payload: Any):
        await self.redis.publish(event_type, json.dumps(payload))

    async def wait_for(self, event_type: str) -> Any:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(event_type)
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await pubsub.unsubscribe(event_type)
                return data

    async def listen(self, event_type: str):
        """
        Continuously yields messages from the specified channel.
        """
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(event_type)
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = json.loads(message['data'])
                    yield data
        finally:
            await pubsub.unsubscribe(event_type)

