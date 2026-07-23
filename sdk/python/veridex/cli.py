import click
import json
import os
from pathlib import Path
from veridex.client import Client

CONFIG_DIR = Path.home() / ".veridex"
CONFIG_FILE = CONFIG_DIR / "config.json"

def get_client() -> Client:
    api_key = None
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            api_key = config.get("token")
    
    # Allow override via env
    api_key = os.environ.get("VERIDEX_API_KEY", api_key)
    base_url = os.environ.get("VERIDEX_BASE_URL", "http://localhost:8000")
    
    return Client(api_key=api_key, base_url=base_url)

@click.group()
def cli():
    """Veridex Platform CLI"""
    pass

@cli.command()
@click.option("--token", required=True, help="Your Veridex API token")
def login(token: str):
    """Authenticate with the Veridex platform."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"token": token}, f)
    click.secho(f"Successfully logged in.", fg="green")

@cli.group()
def agent():
    """Manage and run Veridex Agents"""
    pass

@agent.command()
@click.option("--goal", required=True, help="The goal for the agent to achieve")
def run(goal: str):
    """Run an agent workflow and stream the reasoning traces."""
    client = get_client()
    click.secho(f"Submitting goal: '{goal}'...", fg="cyan")
    
    try:
        response = client.agents.run(goal=goal)
        click.secho("Goal submitted successfully. Streaming timeline...\n", fg="green")
        
        for event in client.agents.stream_timeline():
            event_type = event.get('event')
            data = event.get('data', {})
            
            if isinstance(data, dict):
                msg = data.get('message', str(data))
            else:
                msg = str(data)
                
            color = "white"
            if event_type == "task_completed":
                color = "green"
            elif event_type == "task_started":
                color = "yellow"
                
            click.secho(f"[{event_type}] {msg}", fg=color)
            
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")

@cli.group()
def knowledge():
    """Manage Knowledge Graph and Connectors"""
    pass

@knowledge.command()
@click.option("--type", "connector_type", required=True, help="Connector type (e.g. github, filesystem)")
@click.option("--config", required=True, help="JSON configuration string for the connector")
def sync(connector_type: str, config: str):
    """Trigger a background ingestion sync."""
    client = get_client()
    try:
        config_dict = json.loads(config)
        response = client.knowledge.sync_connector(connector_type=connector_type, config=config_dict)
        click.secho(f"Sync job triggered successfully: {response}", fg="green")
    except json.JSONDecodeError:
        click.secho("Error: --config must be a valid JSON string.", fg="red")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")

@cli.group()
def telemetry():
    """View Telemetry and Traces"""
    pass

@telemetry.command()
def list_traces():
    """List recent orchestration traces."""
    client = get_client()
    try:
        traces = client.telemetry.list_traces()
        for trace in traces:
            click.echo(f"Trace ID: {trace.get('id')} | Status: {trace.get('status')}")
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")

if __name__ == "__main__":
    cli()
