"""
Example Custom Tool for Hot-Reloading
======================================

This tool will be automatically discovered and loaded by agents when placed
in the ./tools/ directory. You can modify this file while your agent is running,
and the changes will be picked up automatically (hot-reloading).

To use hot-reloading:
    agent = Agent(hot_reload=True)

The agent will automatically discover all tools in the ./tools/ directory.
"""

from strands import tool
from datetime import datetime


@tool
def greet_user(name: str) -> str:
    """
    Generate a friendly greeting for a user.

    Args:
        name: The name of the user to greet

    Returns:
        A personalized greeting message
    """
    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:
        time_of_day = "Good morning"
    elif 12 <= current_hour < 18:
        time_of_day = "Good afternoon"
    else:
        time_of_day = "Good evening"

    return f"{time_of_day}, {name}! Welcome to Strands Agents."


@tool
def is_palindrome(text: str) -> bool:
    """
    Check if a text string is a palindrome (reads the same forwards and backwards).

    Args:
        text: The text to check

    Returns:
        True if the text is a palindrome, False otherwise
    """
    # Remove spaces and convert to lowercase for comparison
    clean_text = text.replace(" ", "").lower()
    return clean_text == clean_text[::-1]


@tool
def character_frequency(text: str) -> dict:
    """
    Count the frequency of each character in a text string.

    Args:
        text: The text to analyze

    Returns:
        A dictionary mapping each character to its frequency count
    """
    frequency = {}
    for char in text:
        if char in frequency:
            frequency[char] += 1
        else:
            frequency[char] = 1
    return frequency


@tool
def factorial(n: int) -> int:
    """
    Calculate the factorial of a number.

    Args:
        n: A non-negative integer

    Returns:
        The factorial of n (n!)

    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")

    if n == 0 or n == 1:
        return 1

    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


@tool
def list_summary(numbers: list) -> dict:
    """
    Generate summary statistics for a list of numbers.

    Args:
        numbers: A list of numeric values

    Returns:
        A dictionary with sum, average, min, max, and count
    """
    if not numbers:
        return {
            "count": 0,
            "sum": 0,
            "average": 0,
            "min": None,
            "max": None
        }

    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }


# You can add more custom tools here!
# Each function decorated with @tool will be automatically discovered.
