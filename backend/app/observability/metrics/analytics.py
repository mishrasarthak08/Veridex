from typing import Dict, Any

class CostAnalytics:
    def __init__(self):
        self.usage = {}

    def log_usage(self, user_id: str, tokens: int, cost: float):
        if user_id not in self.usage:
            self.usage[user_id] = {"total_tokens": 0, "total_cost": 0.0}
        
        self.usage[user_id]["total_tokens"] += tokens
        self.usage[user_id]["total_cost"] += cost

    def get_dashboard(self) -> Dict[str, Any]:
        return {
            "total_users_tracked": len(self.usage),
            "usage": self.usage
        }
