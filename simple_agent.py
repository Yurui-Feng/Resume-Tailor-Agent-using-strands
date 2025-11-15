"""
Simple Strands Agent Example
=============================

This is the absolute simplest Strands agent you can create.
It demonstrates the basic agent functionality with minimal configuration.

Usage:
    python simple_agent.py
"""

from strands import Agent
import logging

# Optional: Enable debug logging to see what's happening under the hood
# Uncomment the lines below to see detailed logs
# logging.basicConfig(level=logging.INFO)
# logging.getLogger("strands").setLevel(logging.DEBUG)


def main():
    print("=" * 60)
    print("Strands Agent - Simple Example")
    print("=" * 60)
    print()

    # Create the simplest possible agent
    # By default, it uses Amazon Bedrock with Claude Sonnet
    print("Creating agent...")
    agent = Agent()
    print("Agent created successfully!")
    print()

    # Ask the agent a question
    print("Asking the agent about agentic AI...")
    print("-" * 60)

    response = agent("Tell me about agentic AI in 2-3 sentences.")

    print()
    print("Agent Response:")
    print("-" * 60)
    print(response)
    print()

    # Try another question
    print()
    print("Asking about the Strands framework...")
    print("-" * 60)

    response2 = agent("What is the Strands Agents SDK?")

    print()
    print("Agent Response:")
    print("-" * 60)
    print(response2)
    print()

    print("=" * 60)
    print("Example complete!")
    print("=" * 60)


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
