import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class PromptStore:
    def __init__(self, storage_dir: str = "prompts"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

    def save_prompt(self, name: str, version: str, template: str, owner: str):
        prompt_data = {
            "name": name,
            "version": version,
            "template": template,
            "owner": owner
        }
        file_path = self.storage_dir / f"{name}_v{version}.yaml"
        with open(file_path, "w") as f:
            yaml.dump(prompt_data, f)
            
    def get_prompt(self, name: str, version: str) -> Optional[str]:
        file_path = self.storage_dir / f"{name}_v{version}.yaml"
        if file_path.exists():
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                return data.get("template")
        return None
