from typing import Dict, Type
from .base import BaseTool

class ToolRegistry:
    """
    Central registry for all AI tools.
    Agents retrieve tools from here, and it enforces permissions/schemas.
    """
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool_instance: BaseTool):
        self._tools[tool_instance.name] = tool_instance

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise ValueError(f"Tool {name} not found in registry.")
        return self._tools[name]
        
    def get_litellm_tools(self) -> list[dict]:
        """Returns tools in the OpenAI/LiteLLM standard tool schema format."""
        litellm_tools = []
        for name, instance in self._tools.items():
            litellm_tools.append({
                "type": "function",
                "function": {
                    "name": instance.name,
                    "description": instance.description,
                    "parameters": instance.schema.model_json_schema()
                }
            })
        return litellm_tools

tool_registry = ToolRegistry()
