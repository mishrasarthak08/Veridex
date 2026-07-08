class AgentClient:
    def __init__(self, client):
        self.client = client

    def run(self, goal: str, tenant_id: str = "default") -> dict:
        """
        Runs an agent workflow. 
        In a real SDK, this would make an HTTP request to self.client.base_url
        """
        return {
            "status": "success",
            "goal": goal,
            "message": "Workflow started successfully."
        }
