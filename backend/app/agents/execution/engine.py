import json
import asyncio
from typing import Dict, Any, List
from litellm import acompletion
from app.agents.registry.tools import global_tools
from app.agents.execution.memory import WorkspaceMemory
from app.core.config import settings

class AgentExecutor:
    """
    Core Execution loop for an Agent.
    Implements a simple ReAct loop using the provided model and tools.
    """
    def __init__(self, workspace_id: str, model_name: str = "gemini/gemini-2.5-flash"):
        self.workspace_id = workspace_id
        self.model_name = model_name
        self.memory = WorkspaceMemory(workspace_id)
        # Using LiteLLM, we pass the gemini prefix for Google models
        self.max_iterations = 10

    async def execute_task(self, task: str) -> str:
        """
        Executes a task using the ReAct loop and dynamically discovered tools.
        """
        system_prompt = (
            "You are an autonomous agent.\n"
            "You must complete the given task by using the available tools.\n"
            "When you have the final answer, summarize it clearly.\n"
            "Do not give up. If a tool fails, try another approach."
        )
        
        # Load long term context if we had a retriever, here we just use WorkspaceMemory
        workspace_context = await self.memory.get_context()
        
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\nWorkspace Context:\n{workspace_context}"},
            {"role": "user", "content": task}
        ]
        
        tools_schema = global_tools.get_all_schemas()
        
        for i in range(self.max_iterations):
            response = await acompletion(
                model=self.model_name,
                messages=messages,
                tools=tools_schema if tools_schema else None,
                tool_choice="auto" if tools_schema else None
            )
            
            message = response.choices[0].message
            messages.append(message.model_dump())
            
            if not message.tool_calls:
                # Agent has finished and provided a final answer
                final_answer = message.content or ""
                # Save the final answer to memory as a fact
                await self.memory.add_fact(f"Task completed: {task}\nResult: {final_answer}")
                return final_answer
                
            # Execute tool calls
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                tool_func = global_tools.get_tool(func_name)
                
                if tool_func:
                    try:
                        # In a real app we might need to handle async tools vs sync tools
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(**func_args)
                        else:
                            result = tool_func(**func_args)
                            
                        # Make sure result is a string for the LLM
                        result_str = str(result)
                    except Exception as e:
                        result_str = f"Error executing {func_name}: {e}"
                else:
                    result_str = f"Error: Tool {func_name} not found."
                    
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": result_str
                })
                
        return "Error: Maximum iterations reached without a final answer."
