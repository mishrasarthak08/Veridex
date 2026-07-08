"""
Example: Multi-Agent Workflow
Demonstrates orchestrating a Planner Agent and multiple Worker Agents.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))
from veridex import Client

def main():
    client = Client(api_key="demo")
    
    # Step 1: Planner Agent decomposes the task
    print("1. Submitting goal to Planner Agent...")
    planner_response = client.agents.run(
        goal="Research competitive pricing and write a summary report."
    )
    
    # Step 2: In a real system, the orchestrator handles this. 
    # Here we simulate the client-side view of the orchestration.
    tasks = ["Research competitive pricing", "Write a summary report"]
    
    for task in tasks:
        print(f"2. Dispatching Worker Agent for task: '{task}'")
        client.agents.run(goal=task)
        
    print("Workflow complete.")

if __name__ == "__main__":
    main()
