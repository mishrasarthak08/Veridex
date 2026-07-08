from typing import List, Dict, Any, AsyncGenerator, Optional
from app.ai.config import ai_config
from app.ai.providers import ProviderFactory
from app.ai.events import ai_event_bus
import time

class ModelRouter:
    def __init__(self):
        pass

    def _resolve_model(self, task_type: str = "default") -> str:
        """Resolve the best model for the given task type using routing config."""
        routing_map = ai_config.routing
        # Fallback to default if task_type not explicitly configured
        model_name = routing_map.get(task_type, routing_map.get("default", "gpt-4o"))
        return model_name

    def _get_provider_for_model(self, model_name: str):
        model_info = ai_config.models.get(model_name)
        if not model_info:
            raise ValueError(f"Model {model_name} not found in models.yaml")
        provider_name = model_info.get("provider")
        return ProviderFactory.get_provider(provider_name)

    async def generate(self, messages: List[Dict[str, Any]], task_type: str = "default", tools: Optional[List[Dict[str, Any]]] = None, **kwargs) -> Dict[str, Any]:
        model_name = self._resolve_model(task_type)
        provider = self._get_provider_for_model(model_name)

        start_time = time.time()
        
        try:
            response = await provider.generate(model=model_name, messages=messages, tools=tools, **kwargs)
            latency = (time.time() - start_time) * 1000
            
            # Emit Telemetry Event
            await ai_event_bus.publish("ModelCalled", {
                "provider": provider.provider_name,
                "model": model_name,
                "task_type": task_type,
                "latency_ms": latency,
                "success": True,
                "usage": response.get("usage", {})
            })
            return response
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            await ai_event_bus.publish("ModelCalled", {
                "provider": provider.provider_name,
                "model": model_name,
                "task_type": task_type,
                "latency_ms": latency,
                "success": False,
                "error": str(e)
            })
            raise e

router = ModelRouter()
