# Peargent

[![PyPI version](https://badge.fury.io/py/peargent.svg)](https://badge.fury.io/py/peargent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern Python framework for building intelligent AI agents with advanced tracing, history management, and seamless LLM integration.

## Features

- **Advanced Tracing** - Track every action, decision, and API call with detailed telemetry and database persistence
- **Smart History Management** - Built-in conversation history with intelligent context windowing and buffer management
- **Multi-LLM Support** - Seamlessly switch between OpenAI, Anthropic, Groq, and more
- **Type-Safe Tools** - Pydantic-powered tool system with automatic validation
- **Agent Pools** - Run multiple agents concurrently with shared context
- **Streaming Support** - Real-time streaming responses with event handling
- **Cost Tracking** - Monitor token usage and costs across all LLM providers

## Installation

```bash
pip install peargent
```

### Optional Dependencies

For PostgreSQL database tracing:
```bash
pip install peargent[postgresql]
```

## Quick Start

### Basic Agent

```python
from peargent import create_agent
from peargent.models import groq

agent = create_agent(
    name="assistant",
    persona="You are a helpful AI assistant.",
    model=groq("llama-3.3-70b-versatile")
)

result = agent.run("What is the capital of France?")
print(result)
```

### Agent with Tools

```python
from peargent import create_agent, tool
from peargent.models import openai

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny and 72 degrees F"

agent = create_agent(
    name="weather_bot",
    persona="You are a weather assistant.",
    model=openai("gpt-4"),
    tools=[get_weather]
)

result = agent.run("What's the weather in San Francisco?")
print(result)
```

### Database Tracing

```python
from peargent import create_agent
from peargent.models import openai
from peargent.telemetry import DatabaseTracer

# SQLite
tracer = DatabaseTracer(
    db_type="sqlite",
    db_path="./traces.db"
)

agent = create_agent(
    name="traced_agent",
    persona="You are a helpful assistant.",
    model=openai("gpt-4o"),
    tracer=tracer
)

result = agent.run("Explain quantum computing")
# All traces automatically saved to database
```

### Streaming Responses

```python
from peargent import create_agent
from peargent.models import openai

agent = create_agent(
    name="streaming_agent",
    persona="You are a helpful assistant.",
    model=openai("gpt-4o")
)

for chunk in agent.stream("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Agent Pools

```python
from peargent import AgentPool
from peargent.models import openai, groq

pool = AgentPool(
    agents=[
        {"name": "researcher", "persona": "Research expert", "model": openai("gpt-4o")},
        {"name": "writer", "persona": "Content writer", "model": groq("llama-3.3-70b-versatile")}
    ]
)

results = pool.run_all("Explain artificial intelligence")
for agent_name, result in results.items():
    print(f"{agent_name}: {result}")
```

## Core Concepts

### Agents
Agents are autonomous entities that can process requests, use tools, maintain conversation history, and interact with LLMs.

### Tools
Tools are Python functions decorated with `@tool` that agents can call. They're automatically validated using Pydantic schemas.

### Tracing
The telemetry system tracks all agent activities including LLM calls, tool usage, token consumption, and costs. Traces can be saved to SQLite or PostgreSQL databases.

### History Management
Built-in conversation history with configurable buffer sizes, context windowing, and automatic truncation strategies.

### Models
Unified interface for multiple LLM providers:
- `openai()` - OpenAI models
- `anthropic()` - Anthropic Claude models
- `groq()` - Groq models
- More providers coming soon

## Documentation

Full documentation is available at [your-docs-url-here]

## Examples

Check out the `/examples` directory for more comprehensive examples:
- Multi-agent pools
- Database tracing
- Streaming responses
- Custom tools
- Cost tracking
- And more!

## Requirements

- Python >= 3.9
- requests >= 2.31
- python-dotenv >= 1.0
- pydantic >= 2.0

## License

MIT License - see [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created by [Quanta-Naut](https://github.com/Quanta-Naut)

## Links

- [GitHub Repository](https://github.com/Quanta-Naut/peargent)
- [Documentation](your-docs-url-here)
- [PyPI Package](https://pypi.org/project/peargent/)
- [Issue Tracker](https://github.com/Quanta-Naut/peargent/issues)
