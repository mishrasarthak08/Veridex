from .agents import AgentClient
from .knowledge import KnowledgeClient
from .telemetry import TelemetryClient
from .evaluations import EvaluationsClient
from .projects import ProjectsClient

class Client:
    """
    Main Veridex SDK Client.
    """
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.agents = AgentClient(self)
        self.knowledge = KnowledgeClient(self)
        self.telemetry = TelemetryClient(self)
        self.evaluations = EvaluationsClient(self)
        self.projects = ProjectsClient(self)
