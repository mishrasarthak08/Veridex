import asyncio
from typing import Dict, Any, List
from app.agents.planner.engine import PlanningEngine, TaskNode
from app.agents.scheduler.queue import TaskScheduler
from app.agents.communication.bus import AgentBus

class Orchestrator:
    def __init__(self):
        self.planner = PlanningEngine()
        self.scheduler = TaskScheduler()
        self.bus = AgentBus()
        self.tasks: Dict[str, TaskNode] = {}
        self.completed_tasks = set()

    async def execute_goal(self, goal: str):
        print(f"[Orchestrator] Decomposing goal: {goal}")
        dag = await self.planner.decompose(goal)
        
        dag_info = [{"id": task.id, "dependencies": task.dependencies} for task in dag]
        await self.bus.publish("system_events", {"message": f"Decomposed goal into {len(dag)} tasks", "dag": dag_info})
        
        for task in dag:
            self.tasks[task.id] = task
            if not task.dependencies:
                await self.scheduler.enqueue(task)
                
        # Wait for all tasks to complete
        while len(self.completed_tasks) < len(self.tasks):
            completed_task_id = await self.bus.wait_for("TaskCompleted")
            self.completed_tasks.add(completed_task_id)
            print(f"[Orchestrator] Task {completed_task_id} completed.")
            
            # Check for newly unblocked tasks
            for task in self.tasks.values():
                if task.id not in self.completed_tasks:
                    # If all dependencies are met, enqueue
                    if all(dep in self.completed_tasks for dep in task.dependencies):
                        # Ensure we don't enqueue multiple times
                        if not self.scheduler.is_queued(task.id):
                            await self.scheduler.enqueue(task)
                            
        await self.bus.publish("system_events", {"message": "Goal completed successfully.", "goal": goal})
        print(f"[Orchestrator] Goal completed successfully.")
