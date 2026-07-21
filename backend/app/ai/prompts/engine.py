from pathlib import Path
from typing import Dict, Any, Tuple
import hashlib

PROMPT_DIR = Path(__file__).resolve().parent

class PromptEngine:
    """
    Engine to manage, version, and load prompts.
    Later this can be connected to PostgreSQL for dynamic prompt updates.
    """
    def __init__(self):
        self.prompts_cache = {}
        self.versions_cache = {}

    def get_prompt(self, template_name: str, **kwargs) -> str:
        content, _ = self.get_prompt_with_version(template_name, **kwargs)
        return content

    def get_prompt_with_version(self, template_name: str, **kwargs) -> Tuple[str, str]:
        if template_name not in self.prompts_cache:
            file_path = PROMPT_DIR / f"{template_name}.txt"
            if not file_path.exists():
                # For Sprint 2 testing without a real filesystem prompt
                fake_content = f"System Prompt: {template_name} (Not found on disk)"
                self.prompts_cache[template_name] = fake_content
                self.versions_cache[template_name] = hashlib.sha256(fake_content.encode()).hexdigest()[:8]
            else:
                with open(file_path, "r") as f:
                    content = f.read()
                    self.prompts_cache[template_name] = content
                    self.versions_cache[template_name] = hashlib.sha256(content.encode()).hexdigest()[:8]
        
        template = self.prompts_cache[template_name]
        version = self.versions_cache[template_name]
        try:
            return template.format(**kwargs), version
        except KeyError as e:
            raise ValueError(f"Missing required parameter for prompt {template_name}: {e}")

prompt_engine = PromptEngine()
