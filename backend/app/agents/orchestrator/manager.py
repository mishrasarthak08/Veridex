import asyncio
from typing import Dict, Any, List
from app.agents.planner.engine import PlanningEngine, TaskNode
from app.agents.scheduler.queue import TaskScheduler
from app.agents.communication.bus import AgentBus
from app.observability.tracing.recorder import ExecutionRecorder

# Use a global or shared recorder for this demo setup
global_recorder = ExecutionRecorder()

class Orchestrator:
    def __init__(self):
        self.planner = PlanningEngine()
        self.scheduler = TaskScheduler()
        self.bus = AgentBus()
        self.tasks: Dict[str, TaskNode] = {}
        self.completed_tasks = set()
        self.recorder = global_recorder

    async def execute_goal(self, goal: str):
        print(f"[Orchestrator] Decomposing goal: {goal}")
        
        # Start Trace
        trace_id = self.recorder.start_trace(goal=goal)
        planner_span_id = self.recorder.start_span(trace_id, name="PlanningEngine.decompose")
        
        dag = await self.planner.decompose(goal)
        
        # End Planner Span
        self.recorder.end_span(trace_id, planner_span_id, metadata={"task_count": len(dag)})
        
        dag_info = [{"id": task.id, "dependencies": task.dependencies} for task in dag]
        await self.bus.publish("system_events", {"event": "dag_created", "message": f"Decomposed goal into {len(dag)} tasks", "dag": dag_info})
        
        # Span map to keep track of tasks
        task_spans = {}
        
        for task in dag:
            self.tasks[task.id] = task
            if not task.dependencies:
                span_id = self.recorder.start_span(trace_id, name=f"Task:{task.id}")
                task_spans[task.id] = span_id
                await self.scheduler.enqueue(task)
                
        # Wait for all tasks to complete
        while len(self.completed_tasks) < len(self.tasks):
            completed_task_id = await self.bus.wait_for("TaskCompleted")
            self.completed_tasks.add(completed_task_id)
            print(f"[Orchestrator] Task {completed_task_id} completed.")
            
            if completed_task_id in task_spans:
                self.recorder.end_span(trace_id, task_spans[completed_task_id], metadata={"status": "completed"})
            
            # Check for newly unblocked tasks
            for task in self.tasks.values():
                if task.id not in self.completed_tasks:
                    # If all dependencies are met, enqueue
                    if all(dep in self.completed_tasks for dep in task.dependencies):
                        # Ensure we don't enqueue multiple times
                        if not self.scheduler.is_queued(task.id):
                            span_id = self.recorder.start_span(trace_id, name=f"Task:{task.id}")
                            task_spans[task.id] = span_id
                            await self.scheduler.enqueue(task)
                            
        await self.bus.publish("system_events", {"event": "goal_completed", "message": "Goal completed successfully.", "goal": goal})
        print(f"[Orchestrator] Goal completed successfully.")
        
        # End Trace
        self.recorder.end_trace(trace_id)
