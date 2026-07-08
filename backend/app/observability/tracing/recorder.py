import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .models import AITrace, TraceSpan

class ExecutionRecorder:
    """
    In-memory / JSONL recorder for AI tracing (OpenTelemetry-like).
    """
    def __init__(self, log_path: str = "traces.jsonl"):
        self.log_path = log_path
        self.active_traces: Dict[str, AITrace] = {}

    def start_trace(self, goal: str) -> str:
        trace_id = str(uuid.uuid4())
        self.active_traces[trace_id] = AITrace(
            trace_id=trace_id,
            goal=goal,
            start_time=datetime.now(timezone.utc)
        )
        return trace_id

    def start_span(self, trace_id: str, name: str, parent_id: Optional[str] = None) -> str:
        span_id = str(uuid.uuid4())
        if trace_id in self.active_traces:
            span = TraceSpan(
                span_id=span_id,
                parent_id=parent_id,
                name=name,
                start_time=datetime.now(timezone.utc)
            )
            self.active_traces[trace_id].spans.append(span)
        return span_id

    def end_span(self, trace_id: str, span_id: str, metadata: Dict[str, Any] = None):
        if trace_id in self.active_traces:
            for span in self.active_traces[trace_id].spans:
                if span.span_id == span_id:
                    span.end_time = datetime.now(timezone.utc)
                    if metadata:
                        span.metadata.update(metadata)
                    break

    def end_trace(self, trace_id: str, total_cost: float = 0.0, total_tokens: int = 0):
        if trace_id in self.active_traces:
            trace = self.active_traces[trace_id]
            trace.end_time = datetime.now(timezone.utc)
            trace.total_cost = total_cost
            trace.total_tokens = total_tokens
            
            # Flush to file
            with open(self.log_path, "a") as f:
                f.write(trace.model_dump_json() + "\n")
            
            del self.active_traces[trace_id]
