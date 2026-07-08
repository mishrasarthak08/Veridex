import time
import requests
import random

def trigger_chaos():
    """
    Simulates random infrastructure failures for Chaos Engineering.
    In a real Kubernetes environment, this script would kill pods or 
    add network latency via Istio fault injection.
    """
    print("Starting Chaos Engineering Routine...")
    
    events = [
        "Killing Redis Pod...",
        "Injecting 5s latency into Qdrant...",
        "Simulating LLM Provider 503 Outage...",
        "Terminating 2 Agent Workers..."
    ]
    
    event = random.choice(events)
    print(f"CHAOS EVENT: {event}")
    
    # Simulate the event applying
    time.sleep(2)
    
    print("Chaos Event applied. Veridex should automatically retry or trip circuit breakers.")

if __name__ == "__main__":
    trigger_chaos()
