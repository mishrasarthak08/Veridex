class HumanApprovalEngine:
    @staticmethod
    def requires_approval(cost: float, tool_name: str, environment: str = "production") -> bool:
        """
        Returns True if a manager must approve the action.
        """
        if cost > 25.0:
            return True
            
        if tool_name == "send_email":
            return True
            
        if tool_name == "execute_sql" and environment == "production":
            return True
            
        return False
