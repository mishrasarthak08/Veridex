from pathlib import Path
from typing import Dict, Any

PROMPT_DIR = Path(__file__).resolve().parent

class PromptEngine:
    """
    Engine to manage, version, and load prompts.
    Later this can be connected to PostgreSQL for dynamic prompt updates.
    """
    def __init__(self):
        self.prompts_cache = {}

    def get_prompt(self, template_name: str, **kwargs) -> str:
        if template_name not in self.prompts_cache:
            file_path = PROMPT_DIR / f"{template_name}.txt"
            if not file_path.exists():
                # For Sprint 2 testing without a real filesystem prompt
                return f"System Prompt: {template_name} (Not found on disk)"
            with open(file_path, "r") as f:
                self.prompts_cache[template_name] = f.read()
        
        template = self.prompts_cache[template_name]
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter for prompt {template_name}: {e}")

prompt_engine = PromptEngine()
