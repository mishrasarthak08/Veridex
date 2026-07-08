import yaml
import os
from pathlib import Path
from typing import Dict, Any

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"

def load_yaml_config(filename: str) -> Dict[str, Any]:
    file_path = CONFIG_DIR / filename
    if not file_path.exists():
        return {}
    with open(file_path, "r") as f:
        return yaml.safe_load(f) or {}

class AIConfig:
    def __init__(self):
        self.providers = load_yaml_config("providers.yaml")
        self.models = load_yaml_config("models.yaml")
        self.routing = load_yaml_config("routing.yaml")
        self.tools = load_yaml_config("tools.yaml")
        self.agents = load_yaml_config("agents.yaml")

    def reload(self):
        self.providers = load_yaml_config("providers.yaml")
        self.models = load_yaml_config("models.yaml")
        self.routing = load_yaml_config("routing.yaml")
        self.tools = load_yaml_config("tools.yaml")
        self.agents = load_yaml_config("agents.yaml")

ai_config = AIConfig()
