import yaml

class PolicyEngine:
    """
    Evaluates YAML-based declarative rules for Agent tool execution.
    """
    def __init__(self, raw_yaml: str):
        self.policy = yaml.safe_load(raw_yaml)

    def evaluate(self, tool_name: str) -> bool:
        """
        Returns True if the tool execution is allowed by the policy, False otherwise.
        """
        allow_list = self.policy.get("allow", [])
        deny_list = self.policy.get("deny", [])

        if tool_name in deny_list:
            return False
        
        if "*" in allow_list or tool_name in allow_list:
            return True
            
        return False
