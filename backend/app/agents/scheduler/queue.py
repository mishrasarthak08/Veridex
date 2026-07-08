import asyncio
from app.agents.planner.engine import TaskNode

class TaskScheduler:
    """
    In-memory task scheduler using asyncio.Queue.
    In the future, this wraps Celery or Temporal.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.queued_ids = set()

    async def enqueue(self, task: TaskNode):
        await self.queue.put(task)
        self.queued_ids.add(task.id)
        print(f"[Scheduler] Enqueued task: {task.id} for {task.agent_role}")

    def is_queued(self, task_id: str) -> bool:
        return task_id in self.queued_ids
        
    async def get_next(self) -> TaskNode:
        return await self.queue.get()
