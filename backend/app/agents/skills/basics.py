from app.agents.registry.tools import tool

@tool
def calculate_math(expression: str) -> str:
    """
    Evaluates a simple mathematical expression.
    Useful for basic arithmetic.
    """
    try:
        # Extremely dangerous in production, but okay for a trusted sandbox
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: {e}"

@tool
def search_web(query: str) -> str:
    """
    Searches the web for current information.
    Use this when you need up to date facts.
    """
    # Placeholder for a real web search tool like Tavily or Serper
    return f"Simulated search results for: {query}"
