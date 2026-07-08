from locust import HttpUser, task, between

class VeridexAgentUser(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def check_health(self):
        self.client.get("/health")

    @task(1)
    def submit_goal(self):
        # Simulate pushing a heavy goal to the agent orchestrator
        self.client.post("/agents/goal", json={
            "goal": "Generate a full financial report for Q4",
            "context": "Needs rigorous data fetching"
        })
