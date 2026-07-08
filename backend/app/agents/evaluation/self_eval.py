from typing import Dict, Any
import time

class AgentEvaluator:
    def __init__(self):
        self.metrics = {}

    def log_execution(self, agent_name: str, task_id: str, duration: float, tokens: int, success: bool):
        if agent_name not in self.metrics:
            self.metrics[agent_name] = {"total_tasks": 0, "successes": 0, "total_duration": 0.0, "total_tokens": 0}
            
        metrics = self.metrics[agent_name]
        metrics["total_tasks"] += 1
        metrics["successes"] += 1 if success else 0
        metrics["total_duration"] += duration
        metrics["total_tokens"] += tokens
        
    def get_agent_score(self, agent_name: str) -> float:
        metrics = self.metrics.get(agent_name)
        if not metrics or metrics["total_tasks"] == 0:
            return 0.0
        return metrics["successes"] / metrics["total_tasks"]
