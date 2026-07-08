import os
import sys

# Add local sdk path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))

from veridex import Client

def main():
    # Initialize the Veridex client
    client = Client(api_key="your_api_key_here")
    
    # Run a simple chat agent
    print("Sending workflow to Veridex...")
    response = client.agents.run(
        goal="Summarize the latest trends in AI agents based on our knowledge base.",
        tenant_id="acme_corp"
    )
    
    print(f"Status: {response['status']}")
    print(f"Message: {response['message']}")

if __name__ == "__main__":
    main()
