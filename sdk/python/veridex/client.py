from .agents import AgentClient

class Client:
    """
    Main Veridex SDK Client.
    """
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.agents = AgentClient(self)
