# Resume Tailor Agent

An intelligent AI agent built with [Strands Agents SDK](https://strandsagents.com) that tailors your LaTeX resume to specific job postings while preserving formatting and maintaining accuracy.

## Features

🎯 **Job-Focused Tailoring**
- Analyzes job postings to extract key requirements
- Matches your experience to job needs
- Emphasizes relevant skills and projects
- Incorporates keywords naturally for ATS optimization

📝 **LaTeX-Safe Processing**
- Preserves all LaTeX formatting and syntax
- Validates output before saving
- Supports all major LaTeX resume templates (moderncv, res.cls, custom)
- Never breaks document structure

🔄 **Iterative Refinement**
- Supports multiple revision rounds
- Conversational interface for feedback
- Tracks context across iterations
- Suggests improvements before applying

🛠️ **Custom Tools**
- File reading/writing
- LaTeX validation
- Keyword extraction
- Job requirement analysis
- Resume comparison

---

## Quick Start

### Prerequisites

- Python 3.10 or later (You have Python 3.13.9 installed ✓)
- AWS credentials configured (for default Bedrock provider)
- Access to Claude 4 model in Amazon Bedrock

### Installation

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# All dependencies are already installed!
```

### Configuration

Set up your AWS credentials in `.env` file:

```bash
# Use long-term Bedrock API key (recommended)
AWS_BEARER_TOKEN_BEDROCK=your-long-term-api-key
AWS_REGION=us-east-1

# Or use standard AWS credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

**Important**: Make sure you have:
1. A long-term Bedrock API key (not short-term)
2. Model access enabled for Claude 4 in AWS Bedrock console
3. Appropriate region (us-east-1 or us-west-2)

### Usage

1. **Add your resume**:
   ```bash
   # Place your LaTeX resume here
   data/original/resume.tex
   ```

2. **Add job postings**:
   ```bash
   # Save job postings as .txt files
   data/job_postings/ml_engineer_acme.txt
   data/job_postings/software_dev_techcorp.txt
   ```

3. **Open the notebook**:
   ```bash
   jupyter notebook resume_tailor.ipynb
   ```

4. **Run the cells** and start tailoring!

---

## Core Architecture

The framework is built around **three key components**:

1. **Model** - The language model that powers agent reasoning
2. **System Prompt** - Instructions that guide the model's behavior
3. **Tools** - Capabilities that allow agents to take actions

### The Agent Loop

1. Receives user input
2. Processes the input using a language model
3. Decides whether to use tools
4. Executes those tools and receives results
5. Continues reasoning with the new information
6. Produces a final response

### Basic Example

```python
from strands import Agent

# Simplest agent
agent = Agent()
agent("Tell me about agentic AI")
```

### Agent with Custom Tools

```python
from strands import Agent, tool
from strands_tools import calculator, current_time

@tool
def letter_counter(word: str, letter: str) -> int:
    """Count occurrences of a letter in a word."""
    if len(letter) != 1:
        raise ValueError("Letter must be single character")
    return word.lower().count(letter.lower())

agent = Agent(tools=[calculator, current_time, letter_counter])
agent("How many times does 'e' appear in 'development'?")
```

---

## Key Features

### 1. Multiple LLM Providers

- **Amazon Bedrock** (default with Claude Sonnet)
- **Anthropic API** (Claude models)
- **OpenAI**
- **Google Gemini**
- **Ollama** (local development)
- **LlamaAPI**
- Many others via LiteLLM

### 2. Structured Output

Get type-safe, validated responses using Pydantic models:

```python
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: float
    conditions: str
    location: str

agent = Agent(structured_output_model=WeatherResponse)
result = agent("What's the weather in Seattle?")
data = result.structured_output  # Validated Pydantic instance
```

### 3. Tool Execution Modes

- **Concurrent execution** (default) - Tools run in parallel
- **Sequential execution** - Tools run one after another
- **Direct method calls**: `agent.tool.tool_name(param="value")`
- **Natural language invocation**

### 4. MCP Integration

Access thousands of pre-built tools via Model Context Protocol:

```python
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(...)
tools = mcp_client.list_tools_sync()
agent = Agent(tools=tools)
```

### 5. Session & State Management

Persist conversations across restarts:

- Built-in backends: Local filesystem, Amazon S3
- Amazon Bedrock AgentCore Memory integration
- Custom storage backend support

### 6. Observability & Telemetry

Production-ready monitoring:

- Native OpenTelemetry (OTEL) integration
- Compatible with: Jaeger, Grafana Tempo, AWS X-Ray, Datadog, Langfuse, Opik
- Agent trajectory tracking
- Debug logging support

### 7. Hot-Reloading

- Automatic tool discovery from `./tools/` directory
- Modify tools without restart
- Accelerated development iteration

---

## Examples in This Repository

### 1. `simple_agent.py`
The absolute simplest agent - just a few lines of code to get started.

### 2. `agent_with_tools.py`
Demonstrates custom tool creation and usage with built-in tools.

### 3. `tools/example_tool.py`
A sample custom tool that automatically gets loaded by the agent.

### 4. `getting_started.ipynb`
Interactive Jupyter notebook with step-by-step examples and exercises.

---

## Multi-Agent Orchestration Patterns

Strands supports four primary multi-agent patterns:

### 1. Graph Pattern

Developer-defined flowchart with LLM-driven decisions at each node.

- **Best for:** Interactive support, conditional routing, branching logic
- **Features:** Supports cycles and error-handling edges
- **Example use case:** Customer support with escalation paths

### 2. Swarm Pattern

Autonomous agent collaboration with self-organizing handoffs.

- **Best for:** Multidisciplinary tasks, creative collaboration, diverse expertise
- **Features:** Agents decide which peer to delegate to
- **Example use case:** Research team with specialized analysts

### 3. Workflow Pattern

Pre-defined Task Graph (DAG) with deterministic execution.

- **Best for:** Data pipelines, standard business processes, repeatable operations
- **Features:** No cycles; supports parallel execution
- **Example use case:** ETL pipeline, document processing

### 4. Agents-as-Tools Pattern

Hierarchical delegation where agents call other specialized agents.

- **Best for:** Layered processing, executive-level orchestration
- **Features:** Parent agent delegates to child agents as tools
- **Example use case:** Multi-stage data analysis with specialized processors

---

## Learning Resources

### Official Documentation

- **Main site:** https://strandsagents.com
- **Latest docs:** https://strandsagents.com/latest/documentation/docs/
- **Quickstart:** https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/
- **API Reference:** https://strandsagents.com/latest/documentation/docs/api-reference/agent/

### GitHub Repositories

1. **SDK (Python):** https://github.com/strands-agents/sdk-python
   - 4,000+ stars, 475 forks
   - 73+ contributors, 445 dependent projects
   - Apache 2.0 license

2. **Samples:** https://github.com/strands-agents/samples
   - 509 stars, 258 forks
   - 60+ contributors
   - Real-world examples and tutorials

3. **Documentation:** https://github.com/strands-agents/docs
   - Source for official documentation

4. **Agent Builder:** https://github.com/strands-agents/agent-builder
   - Example agent demonstrating streaming, tool use, and terminal interactivity

### Sample Repository Structure

The official samples repository contains:

**01-tutorials** - Step-by-step guides covering:
- Fundamentals
- Deployment
- Best practices

**02-samples** - Real-world use cases:
- Weather Forecaster (HTTP requests)
- File Operations
- Memory Agent (conversation persistence)
- Multi-modal (multimedia handling)
- Structured Output
- Meta Tooling

**03-integrations** - AWS services and third-party tools:
- MCP Calculator
- Knowledge-Base Workflow

**04-UX-demos** - Full-stack applications:
- CLI Reference Agent
- Interactive terminal agents

**05-agentic-rag** - Advanced RAG patterns

### AWS Blog Posts

1. [Introducing Strands Agents](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)
2. [Technical Deep Dive](https://aws.amazon.com/blogs/machine-learning/strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/)
3. [Strands Agents 1.0 Announcement](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-1-0-production-ready-multi-agent-orchestration-made-simple/)
4. [Multi-Agent Collaboration Patterns](https://aws.amazon.com/blogs/machine-learning/multi-agent-collaboration-patterns-with-strands-agents-and-amazon-nova/)
5. [Model-Driven Approach](https://aws.amazon.com/blogs/opensource/strands-agents-and-the-model-driven-approach/)

### AWS Prescriptive Guidance

- https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-frameworks/strands-agents.html

---

## Deployment Options

### AWS Lambda

- **Type:** Serverless, pay-per-use
- **Timeout:** 30-second (configurable)
- **Architecture:** ARM64 recommended
- **Streaming:** Not supported
- **Best for:** Short-lived, event-driven tasks

### AWS Fargate

- **Type:** Containerized deployment
- **Features:** Long-running agents, streaming response support
- **Best for:** Production web applications, stateful services

### EC2 & EKS

- **Type:** Full infrastructure control
- **Features:** Custom scaling policies, complex deployments
- **Best for:** Enterprise-grade systems

---

## AWS Configuration

### Setting Up AWS Credentials

Strands uses Amazon Bedrock by default. Configure credentials using one of these methods:

#### 1. Environment Variables

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### 2. AWS CLI Configuration

```bash
aws configure
```

#### 3. Bedrock API Keys

```bash
export AWS_BEARER_TOKEN_BEDROCK="your-token"
```

#### 4. IAM Roles (for AWS services)

When running on AWS services (EC2, Lambda, ECS), use IAM roles instead of credentials.

### Using Different Model Providers

```python
from strands import Agent

# Use Anthropic API directly
agent = Agent(
    model_provider="anthropic",
    model_id="claude-3-sonnet-20240229"
)

# Use OpenAI
agent = Agent(
    model_provider="openai",
    model_id="gpt-4"
)

# Use Ollama for local development
agent = Agent(
    model_provider="ollama",
    model_id="llama2"
)
```

---

## Recommended Learning Path

### Week 1: Fundamentals

1. **Day 1-2:** Run the examples in this repo
   - `simple_agent.py`
   - `agent_with_tools.py`
   - Work through `getting_started.ipynb`

2. **Day 3-4:** Build custom tools
   - Create 2-3 custom tools using `@tool` decorator
   - Add them to the `tools/` directory
   - Test hot-reloading functionality

3. **Day 5:** Explore structured output
   - Define Pydantic models for your use case
   - Get type-safe responses from agents

### Week 2: Intermediate

4. **Day 6-7:** Session management
   - Implement conversation persistence
   - Experiment with different storage backends

5. **Day 8-10:** Multi-agent patterns
   - Try Graph pattern for conditional workflows
   - Experiment with Swarm for collaborative tasks
   - Build a simple Workflow for sequential processing

### Week 3: Advanced

6. **Day 11-12:** MCP integration
   - Connect to MCP servers
   - Use pre-built MCP tools

7. **Day 13-14:** Observability
   - Add OpenTelemetry instrumentation
   - View traces in Jaeger or similar

8. **Day 15:** Deployment
   - Deploy a simple agent to AWS Lambda
   - Or containerize and run on Fargate

---

## Troubleshooting

### Common Issues

**Issue:** Agent not responding
- **Solution:** Check AWS credentials and Bedrock model access

**Issue:** Tools not loading from `tools/` directory
- **Solution:** Ensure tools use `@tool` decorator and are valid Python files

**Issue:** Import errors
- **Solution:** Activate virtual environment: `.venv\Scripts\activate`

**Issue:** Jupyter kernel not found
- **Solution:** Kernel is already installed as "Strands Agent SDK" - select it from the kernel menu

### Debug Logging

Enable debug logging to see what's happening:

```python
import logging
logging.getLogger("strands").setLevel(logging.DEBUG)
```

---

## Contributing & Community

- **GitHub Issues:** https://github.com/strands-agents/sdk-python/issues
- **Discussions:** https://github.com/strands-agents/sdk-python/discussions
- **Contributing Guide:** See the main SDK repository

---

## License

This project uses the Strands Agents SDK which is licensed under Apache 2.0.

---

## Next Steps

1. ✅ Environment setup complete
2. ✅ Virtual environment created
3. ✅ Jupyter kernel registered
4. 📝 Run `simple_agent.py` to see your first agent in action
5. 📝 Work through `getting_started.ipynb` for interactive learning
6. 📝 Build your own custom tools
7. 📝 Explore multi-agent patterns
8. 📝 Deploy to production

**Happy building with Strands Agents! 🚀**
