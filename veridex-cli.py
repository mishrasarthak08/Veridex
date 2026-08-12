#!/usr/bin/env python3
import argparse
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def deploy(project_id: str, chaos: bool):
    endpoint = f"{BASE_URL}/projects/{project_id}/chaos" if chaos else f"{BASE_URL}/projects/{project_id}/deploy"
    
    print(f"🚀 Triggering Swarm Deployment for Project: {project_id}")
    if chaos:
        print("⚠️  CHAOS MODE ENABLED")
        
    try:
        response = requests.post(endpoint)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Success! Swarm ID: {data.get('swarm_id')}")
        print(f"💬 Message: {data.get('message')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to deploy swarm: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Veridex CLI - Orchestrate AI Swarms from the Terminal")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy a saved swarm configuration")
    deploy_parser.add_argument("project_id", type=str, help="The ID of the project to deploy")
    deploy_parser.add_argument("--chaos", action="store_true", help="Trigger the swarm in Chaos Engineering mode")
    
    args = parser.parse_args()
    
    if args.command == "deploy":
        deploy(args.project_id, args.chaos)

if __name__ == "__main__":
    main()
