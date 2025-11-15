"""
Strands Agent with Custom Tools Example
========================================

This example demonstrates how to create custom tools and use them with an agent.
Tools allow agents to perform actions and access external functionality.

Usage:
    python agent_with_tools.py
"""

from strands import Agent, tool
from strands_tools import calculator, current_time
import logging

# Optional: Enable debug logging
# logging.basicConfig(level=logging.INFO)
# logging.getLogger("strands").setLevel(logging.DEBUG)


# Define custom tools using the @tool decorator
@tool
def letter_counter(word: str, letter: str) -> int:
    """
    Count the number of occurrences of a letter in a word.

    Args:
        word: The word to search in
        letter: The letter to count (must be a single character)

    Returns:
        The number of times the letter appears in the word (case-insensitive)
    """
    if not isinstance(word, str) or not isinstance(letter, str):
        return 0
    if len(letter) != 1:
        raise ValueError("Letter must be a single character")
    return word.lower().count(letter.lower())


@tool
def word_count(text: str) -> int:
    """
    Count the number of words in a text string.

    Args:
        text: The text to count words in

    Returns:
        The number of words in the text
    """
    if not text:
        return 0
    return len(text.split())


@tool
def reverse_string(text: str) -> str:
    """
    Reverse a string.

    Args:
        text: The text to reverse

    Returns:
        The reversed text
    """
    return text[::-1]


@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert temperature from Celsius to Fahrenheit.

    Args:
        celsius: Temperature in Celsius

    Returns:
        Temperature in Fahrenheit
    """
    return (celsius * 9/5) + 32


@tool
def fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.

    Args:
        n: The position in the Fibonacci sequence (must be >= 0)

    Returns:
        The nth Fibonacci number
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def main():
    print("=" * 70)
    print("Strands Agent - Custom Tools Example")
    print("=" * 70)
    print()

    # Create an agent with custom tools and built-in tools
    print("Creating agent with tools...")
    agent = Agent(
        tools=[
            # Built-in tools from strands-agents-tools
            calculator,
            current_time,
            # Custom tools
            letter_counter,
            word_count,
            reverse_string,
            celsius_to_fahrenheit,
            fibonacci
        ]
    )
    print("Agent created with the following tools:")
    print("  - calculator (built-in)")
    print("  - current_time (built-in)")
    print("  - letter_counter (custom)")
    print("  - word_count (custom)")
    print("  - reverse_string (custom)")
    print("  - celsius_to_fahrenheit (custom)")
    print("  - fibonacci (custom)")
    print()

    # Example 1: Math calculation
    print("-" * 70)
    print("Example 1: Math Calculation")
    print("-" * 70)
    question1 = "What is 3111696 divided by 74088?"
    print(f"Question: {question1}")
    print()
    response1 = agent(question1)
    print(f"Response: {response1}")
    print()

    # Example 2: Letter counting
    print("-" * 70)
    print("Example 2: Letter Counting")
    print("-" * 70)
    question2 = "How many times does the letter 'e' appear in the word 'development'?"
    print(f"Question: {question2}")
    print()
    response2 = agent(question2)
    print(f"Response: {response2}")
    print()

    # Example 3: Word count
    print("-" * 70)
    print("Example 3: Word Count")
    print("-" * 70)
    question3 = "How many words are in this sentence: 'The quick brown fox jumps over the lazy dog'?"
    print(f"Question: {question3}")
    print()
    response3 = agent(question3)
    print(f"Response: {response3}")
    print()

    # Example 4: Temperature conversion
    print("-" * 70)
    print("Example 4: Temperature Conversion")
    print("-" * 70)
    question4 = "What is 25 degrees Celsius in Fahrenheit?"
    print(f"Question: {question4}")
    print()
    response4 = agent(question4)
    print(f"Response: {response4}")
    print()

    # Example 5: Fibonacci sequence
    print("-" * 70)
    print("Example 5: Fibonacci Number")
    print("-" * 70)
    question5 = "What is the 10th Fibonacci number?"
    print(f"Question: {question5}")
    print()
    response5 = agent(question5)
    print(f"Response: {response5}")
    print()

    # Example 6: Multiple tools in one query
    print("-" * 70)
    print("Example 6: Using Multiple Tools")
    print("-" * 70)
    question6 = "What time is it now? Also, reverse the word 'Strands'."
    print(f"Question: {question6}")
    print()
    response6 = agent(question6)
    print(f"Response: {response6}")
    print()

    # Direct tool invocation
    print("-" * 70)
    print("Example 7: Direct Tool Invocation")
    print("-" * 70)
    print("You can also call tools directly without natural language:")
    print()
    direct_result = agent.tool.letter_counter(word="Mississippi", letter="s")
    print(f"agent.tool.letter_counter(word='Mississippi', letter='s') = {direct_result}")
    print()

    print("=" * 70)
    print("Examples complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Try creating your own custom tools")
    print("2. Experiment with different tool combinations")
    print("3. Check out the tools/ directory for hot-reloadable tools")
    print("4. Work through getting_started.ipynb for more examples")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print()
        print("ERROR:", str(e))
        print()
        print("Troubleshooting tips:")
        print("1. Make sure AWS credentials are configured")
        print("2. Ensure you have access to Claude models in Amazon Bedrock")
        print("3. Check your AWS region (default: us-east-1)")
        print("4. Set AWS_DEFAULT_REGION environment variable if needed")
        print()
        print("For more info, see the README.md file")
