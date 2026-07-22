import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.planner.engine import PlanningEngine
from app.agents.execution.engine import AgentExecutor

async def run_test():
    goal = "Research the capital of France and then calculate its population multiplied by 2"
    print(f"Goal: {goal}\n")
    
    # 1. Test Planner
    print("--- 1. Testing Planner (Gemini 2.5 Pro) ---")
    planner = PlanningEngine()
    tasks = await planner.decompose(goal)
    
    print(f"Decomposed into {len(tasks)} tasks:")
    for t in tasks:
        print(f" - ID: {t.id}")
        print(f"   Desc: {t.description}")
        print(f"   Deps: {t.dependencies}")
        print()
        
    if not tasks:
        print("Failed to generate tasks.")
        return
        
    # 2. Test Executor
    first_task = tasks[0]
    print(f"--- 2. Testing Executor (Gemini 2.5 Flash) on Task 1 ---")
    print(f"Task: {first_task.description}")
    
    executor = AgentExecutor(workspace_id="test_workspace")
    result = await executor.execute_task(first_task.description)
    
    print(f"\nFinal Result:\n{result}")

if __name__ == "__main__":
    asyncio.run(run_test())
