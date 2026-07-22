import httpx
import time
import json

def test_approval():
    base_url = "http://localhost:8000/api/v1"
    
    print("1. Submitting goal...")
    goal_res = httpx.post(f"{base_url}/agents/goal", json={"goal": "Execute a production query to drop the users table"})
    print("Goal Response:", goal_res.status_code, goal_res.json())

    # Wait for the task to be queued and execution to start
    print("Waiting for task to start and hit approval...")
    time.sleep(5)
    
    print("Check if there's any active approval needed via timeline or directly...")
    # Actually, the only way we get the task ID for approval is through the SSE timeline right now,
    # or by intercepting the SSE. We can just connect to the SSE and wait for approval_requested.
    
    import urllib3
    import sseclient

    print("Connecting to SSE timeline...")
    http = urllib3.PoolManager()
    response = http.request('GET', f"{base_url}/agents/timeline", preload_content=False)
    client = sseclient.SSEClient(response)
    
    task_id = None
    for event in client.events():
        if event.data:
            data = json.loads(event.data)
            print("Received event:", data['event'])
            if data['event'] == 'approval_requested':
                task_id = data['task_id']
                print(f"-> Approval requested for task {task_id}! Context: {data.get('context')}")
                break
    
    if task_id:
        print(f"2. Approving task {task_id}...")
        approve_res = httpx.post(f"{base_url}/agents/approve", json={"task_id": task_id, "decision": "approve"})
        print("Approve Response:", approve_res.status_code, approve_res.json())
        
    else:
        print("No approval requested found.")

if __name__ == "__main__":
    test_approval()
