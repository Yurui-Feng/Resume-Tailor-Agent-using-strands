# Tools Directory

This directory is for **hot-reloadable custom tools**. Any Python file you place here with tools decorated with `@tool` will be automatically discovered and loaded by agents that have hot-reloading enabled.

## How Hot-Reloading Works

1. Create a Python file in this directory (e.g., `my_tools.py`)
2. Define functions using the `@tool` decorator
3. Create an agent with `hot_reload=True`:

```python
from strands import Agent

agent = Agent(hot_reload=True)
```

4. The agent will automatically discover and use all tools in this directory
5. You can modify the tools while the agent is running, and changes will be picked up automatically!

## Example Tool

See [example_tool.py](example_tool.py) for examples of custom tools.

## Creating Your Own Tools

### Basic Tool Structure

```python
from strands import tool

@tool
def my_custom_tool(param1: str, param2: int) -> str:
    """
    Description of what your tool does.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of what the tool returns
    """
    # Your tool logic here
    result = f"Processed {param1} with {param2}"
    return result
```

### Best Practices

1. **Clear Documentation**: Always include a docstring that explains what the tool does
2. **Type Hints**: Use type hints for parameters and return values
3. **Error Handling**: Handle edge cases and invalid inputs gracefully
4. **Single Responsibility**: Each tool should do one thing well
5. **Descriptive Names**: Use clear, descriptive function names

### Tool Examples by Category

#### Text Processing Tools
- String manipulation (reverse, uppercase, lowercase)
- Text analysis (word count, character frequency)
- Pattern matching (palindrome check, regex search)

#### Math Tools
- Calculations (factorial, fibonacci, prime numbers)
- Statistics (mean, median, mode)
- Unit conversions (temperature, distance, weight)

#### Data Tools
- JSON/CSV parsing
- Data validation
- Format conversion

#### External Integration Tools
- API calls
- Database queries
- File operations

#### Time/Date Tools
- Date formatting
- Time zone conversion
- Calendar operations

## Tool Naming Conventions

- Use `snake_case` for function names
- Use descriptive names that indicate the tool's purpose
- Avoid generic names like `process()` or `handle()`
- Good examples:
  - `calculate_distance()`
  - `fetch_weather_data()`
  - `validate_email()`
  - `convert_markdown_to_html()`

## Testing Your Tools

You can test tools directly:

```python
from strands import Agent

agent = Agent(hot_reload=True)

# Direct invocation
result = agent.tool.my_custom_tool(param1="test", param2=42)
print(result)

# Natural language invocation
response = agent("Use my_custom_tool with 'test' and 42")
```

## Advanced: Async Tools

You can also create async tools:

```python
from strands import tool
import asyncio

@tool
async def async_fetch_data(url: str) -> dict:
    """Fetch data from a URL asynchronously."""
    # Your async code here
    await asyncio.sleep(1)  # Simulate async operation
    return {"status": "success"}
```

## Notes

- Tools in this directory are loaded automatically only when `hot_reload=True`
- Changes to tool files are detected automatically
- If a tool has errors, it will be skipped and a warning will be logged
- You can organize tools into multiple files for better organization
