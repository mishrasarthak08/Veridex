import inspect
import typing
from typing import Callable, Dict, Any, List

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.schemas: Dict[str, Dict[str, Any]] = {}

    def register(self, func: Callable):
        """Register a tool and generate its JSON schema for LLMs."""
        name = func.__name__
        self.tools[name] = func
        self.schemas[name] = self._generate_schema(func)
        return func

    def get_tool(self, name: str) -> Callable:
        return self.tools.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return list(self.schemas.values())

    def _generate_schema(self, func: Callable) -> Dict[str, Any]:
        """Generates OpenAI-compatible function schema from Python type hints."""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or ""
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue
                
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == float:
                    param_type = "number"
                elif getattr(param.annotation, "__origin__", None) == list:
                    param_type = "array"
            
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter {param_name}"
            }
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

# Global registry instance
global_tools = ToolRegistry()

def tool(func: Callable):
    """Decorator to register a function as an LLM tool."""
    return global_tools.register(func)
