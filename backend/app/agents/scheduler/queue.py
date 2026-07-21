from app.agents.planner.engine import TaskNode
from app.workers.tasks.agent import execute_task

class TaskScheduler:
    """
    Celery-backed task scheduler.
    """
    def __init__(self):
        self.queued_ids = set()

    async def enqueue(self, task: TaskNode):
        # We invoke the Celery task directly.
        execute_task.apply_async(args=[task.to_dict()], queue="agent_queue")
        self.queued_ids.add(task.id)
        print(f"[Scheduler] Enqueued task: {task.id} for {task.agent_role} to Celery 'agent_queue'")

    def is_queued(self, task_id: str) -> bool:
        return task_id in self.queued_ids
        
    async def get_next(self) -> TaskNode:
        # In a push-based Celery model, workers pull directly from the broker.
        raise NotImplementedError("Workers now automatically pull from Celery broker.")
