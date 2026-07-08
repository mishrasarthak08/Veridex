from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class TraceSpan(BaseModel):
    span_id: str
    parent_id: Optional[str]
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class AITrace(BaseModel):
    trace_id: str
    goal: str
    start_time: datetime
    end_time: Optional[datetime] = None
    spans: List[TraceSpan] = []
    total_cost: float = 0.0
    total_tokens: int = 0
