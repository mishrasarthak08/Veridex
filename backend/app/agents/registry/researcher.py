from .base import BaseAgent
from app.agents.skills.search import SearchSkill
from app.agents.skills.read_doc import ReadDocumentSkill

class ResearcherAgent(BaseAgent):
    name = "Researcher"
    role = "Senior Technical Researcher"
    goal = "Find accurate, relevant information to answer complex queries."
    backstory = "You are an expert at navigating large codebases and documentation."
    
    def __init__(self):
        super().__init__()
        self.skills = [SearchSkill(), ReadDocumentSkill()]
