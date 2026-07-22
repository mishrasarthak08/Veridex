import logging
import asyncio
from app.ai.events import ai_event_bus
from app.ai.config import ai_config
from app.agents.communication.bus import AgentBus

from app.db.session import AsyncSessionLocal
from app.db.models.telemetry import AILog

logger = logging.getLogger("ai.telemetry")

class TelemetryTracker:
    def __init__(self):
        # Subscribe to ModelCalled events
        ai_event_bus.subscribe("ModelCalled", self.on_model_called)
        self.bus = AgentBus()
        
    async def start_listening(self):
        """Listen to global Redis bus for DAG traces."""
        logger.info("TelemetryTracker starting to listen on system_events")
        async for msg in self.bus.listen("system_events"):
            # If we see dag info or goal completion, record it
            if msg and "dag" in msg:
                logger.info("Telemetry Record: DAG Started", extra={"telemetry": {"type": "dag_start", "dag": msg["dag"]}})
            elif msg and "message" in msg and "completed" in msg["message"]:
                logger.info("Telemetry Record: Goal Completed", extra={"telemetry": {"type": "goal_complete", "goal": msg.get("goal")}})

    async def on_model_called(self, data: dict):
        # Calculate cost based on usage and models.yaml
        usage = data.get("usage", {})
        model = data.get("model")
        
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        model_info = ai_config.models.get(model, {})
        cost_in = model_info.get("cost_per_1k_input", 0) * (prompt_tokens / 1000)
        cost_out = model_info.get("cost_per_1k_output", 0) * (completion_tokens / 1000)
        total_cost = cost_in + cost_out

        data["prompt_tokens"] = prompt_tokens
        data["completion_tokens"] = completion_tokens
        data["cost_usd"] = total_cost

        # Log to structured logger (JSON)
        logger.info("AI Telemetry Record", extra={"telemetry": data})
        
        # Persist to database
        try:
            async with AsyncSessionLocal() as session:
                log_record = AILog(
                    task_id=data.get("task_id"),
                    model=model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_usd=total_cost,
                    latency_ms=data.get("latency_ms", 0),
                    metadata_={"raw": data}
                )
                session.add(log_record)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to persist AILog to database: {e}")

tracker = TelemetryTracker()
