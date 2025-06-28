# Tool Framework Example

from typing import List, Dict
from litecrewai.tools import tool
from litecrewai import Agent

@tool
def web_search(query: str, max_results: int = 5) -> List[Dict]:
    """Search the web for information"""
    # Implementation
    return results

agent = Agent(tools=[web_search, calculator])
result = agent.execute("Search for Python tutorials and calculate 15% of 200")