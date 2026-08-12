from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.telemetry import TelemetryRepository

class TelemetryService:
    def __init__(self, db: AsyncSession):
        self.repo = TelemetryRepository(db)

    async def get_recent_logs(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        logs = await self.repo.get_recent(skip, limit)
        return [
            {
                "id": log.id,
                "task_id": log.task_id,
                "model": log.model,
                "prompt_tokens": log.prompt_tokens,
                "completion_tokens": log.completion_tokens,
                "cost_usd": log.cost_usd,
                "latency_ms": log.latency_ms,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
