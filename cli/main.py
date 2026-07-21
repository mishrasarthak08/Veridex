import argparse
import sys
import os

# Add sdk/python to sys.path so the CLI can import veridex
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))

from veridex import Client

def main():
    parser = argparse.ArgumentParser(prog="veridex", description="Veridex CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # login
    login_parser = subparsers.add_parser("login", help="Authenticate with Veridex")
    login_parser.add_argument("--token", required=True)
    
    # agent run
    agent_parser = subparsers.add_parser("agent-run", help="Run an agent workflow")
    agent_parser.add_argument("--goal", required=True)

    args = parser.parse_args()

    if args.command == "login":
        print(f"Logged in successfully using token: {args.token[:5]}...")
    elif args.command == "agent-run":
        client = Client(api_key="cli_auth")
        print(f"Submitting goal: '{args.goal}'")
        try:
            response = client.agents.run(goal=args.goal)
            print(f"Goal submitted successfully. Streaming timeline...\n")
            
            for event in client.agents.stream_timeline():
                event_type = event.get('event')
                data = event.get('data', {})
                
                if isinstance(data, dict):
                    msg = data.get('message', str(data))
                else:
                    msg = str(data)
                    
                print(f"[{event_type}] {msg}")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
