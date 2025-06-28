# Calculate Tool Example

from litecrewai.tools import tool

@tool
def calculate(expression: str) -> float:
    """
    Safely evaluate mathematical expressions.
    
    Examples:
        calculate("2 + 2") -> 4.0
        calculate("sin(pi/2)") -> 1.0
        calculate("sqrt(16)") -> 4.0
    """
    # Safe implementation here
    pass