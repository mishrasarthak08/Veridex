import json
import redis.asyncio as redis
from typing import Dict, Any, List
from app.core.config import settings

class WorkspaceMemory:
    """
    A shared collaborative memory for agents working on the same goal,
    persisted in Redis for multi-worker scaling.
    """
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id
        # We assume settings has REDIS_URL or default to localhost
        redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379")
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.facts_key = f"workspace:{workspace_id}:facts"
        self.scratch_key = f"workspace:{workspace_id}:scratchpad"
        
    async def add_fact(self, fact: str):
        await self.redis.rpush(self.facts_key, fact)
        
    async def get_context(self) -> str:
        facts = await self.redis.lrange(self.facts_key, 0, -1)
        if not facts:
            return "No facts known."
        return "\n".join([f"- {fact}" for fact in facts])
        
    async def set_var(self, key: str, value: Any):
        # We store complex types as JSON strings
        await self.redis.hset(self.scratch_key, key, json.dumps(value))
        
    async def get_var(self, key: str) -> Any:
        val = await self.redis.hget(self.scratch_key, key)
        if val is None:
            return None
        try:
            return json.loads(val)
        except json.JSONDecodeError:
            return val

