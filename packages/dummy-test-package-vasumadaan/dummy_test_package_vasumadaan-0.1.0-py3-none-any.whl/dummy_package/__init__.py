"""
Dummy Test Package
A simple package for testing private PyPI index
"""

__version__ = "0.1.0"

def greet(name):
    """
    A simple greeting function
    
    Args:
        name (str): The name to greet
        
    Returns:
        str: A greeting message
    """
    message = f"Hello, {name}! This is a dummy package."
    print(message)
    return message


def add(a, b):
    """
    Add two numbers
    
    Args:
        a (int/float): First number
        b (int/float): Second number
        
    Returns:
        int/float: Sum of a and b
    """
    return a + b
