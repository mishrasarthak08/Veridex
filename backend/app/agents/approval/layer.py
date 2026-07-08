import asyncio
from typing import Dict, Any

class HumanApprovalLayer:
    def __init__(self):
        self.pending_approvals: Dict[str, asyncio.Event] = {}
        self.decisions: Dict[str, str] = {}

    async def request_approval(self, task_id: str, context: str) -> str:
        """
        Pauses execution until a human decision is made.
        Returns 'approve', 'reject', or 'revise'.
        """
        print(f"[Approval Layer] Task {task_id} requires human approval. Context: {context}")
        event = asyncio.Event()
        self.pending_approvals[task_id] = event
        
        # Wait for human to hit the REST endpoint
        await event.wait()
        
        decision = self.decisions.pop(task_id, "reject")
        self.pending_approvals.pop(task_id, None)
        return decision

    def submit_decision(self, task_id: str, decision: str):
        if task_id in self.pending_approvals:
            self.decisions[task_id] = decision
            self.pending_approvals[task_id].set()
