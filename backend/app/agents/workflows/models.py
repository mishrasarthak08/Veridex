from pydantic import BaseModel
from typing import List, Dict, Optional

class WorkflowStep(BaseModel):
    name: str
    agent: str
    action: str
    depends_on: Optional[List[str]] = []

class WorkflowDef(BaseModel):
    name: str
    description: str
    steps: List[WorkflowStep]
