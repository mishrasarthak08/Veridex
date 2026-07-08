import json
from typing import Dict, Any, List, Type
from app.ai.router import router
from app.ai.memory.interfaces import ShortTermMemory
from app.ai.tools.registry import tool_registry

class AgentRuntime:
    """
    The orchestration loop.
    Executes tasks, triggers tools, manages memory, and handles reflection.
    """
    def __init__(self, task_type: str = "default"):
        self.task_type = task_type
        self.memory = ShortTermMemory()

    async def execute(self, prompt: str) -> str:
        await self.memory.add("user", prompt)

        # Simple ReAct loop (Max 5 steps to avoid infinite loops)
        for _ in range(5):
            messages = await self.memory.get_all()
            tools = tool_registry.get_litellm_tools()
            
            # Call router (LLM)
            response = await router.generate(
                messages=messages,
                task_type=self.task_type,
                tools=tools if tools else None
            )

            response_message = response["choices"][0]["message"]
            
            # If model wants to call a tool
            if response_message.get("tool_calls"):
                await self.memory.add(
                    "assistant", 
                    response_message.get("content") or "", 
                    tool_calls=response_message["tool_calls"]
                )
                
                for tool_call in response_message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    try:
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        tool_instance = tool_registry.get_tool(tool_name)
                        result = await tool_instance.execute(**tool_args)
                        await self.memory.add("tool", str(result), name=tool_name, tool_call_id=tool_call["id"])
                    except Exception as e:
                        await self.memory.add("tool", f"Error: {str(e)}", name=tool_name, tool_call_id=tool_call["id"])
            else:
                # Task complete
                content = response_message.get("content", "")
                await self.memory.add("assistant", content)
                return content
                
        return "Agent stopped after reaching maximum iterations."
