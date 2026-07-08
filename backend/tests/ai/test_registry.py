import pytest
from app.ai.tools.base import BaseTool
from app.ai.tools.registry import ToolRegistry
from pydantic import BaseModel

class WeatherArgs(BaseModel):
    location: str

class WeatherTool(BaseTool):
    name = "get_weather"
    description = "Get weather"
    schema = WeatherArgs

    async def execute(self, location: str):
        return f"Weather in {location} is sunny"

def test_tool_registry():
    registry = ToolRegistry()
    registry.register(WeatherTool())
    
    tool = registry.get_tool("get_weather")
    assert tool.name == "get_weather"
    
    litellm_schema = registry.get_litellm_tools()
    assert litellm_schema[0]["function"]["name"] == "get_weather"
