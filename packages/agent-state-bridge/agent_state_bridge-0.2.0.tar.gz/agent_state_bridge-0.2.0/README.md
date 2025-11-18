# agent-state-bridge (Python)

Python backend utilities for sharing app state with AI agents. Works with FastAPI, Flask, Django REST Framework, and any Python web framework.

## Installation

```bash
# Basic installation (FastAPI is recommended)
pip install agent-state-bridge[fastapi]

# Or with Flask
pip install agent-state-bridge[flask]

# Or with Django
pip install agent-state-bridge[django]

# Or install all
pip install agent-state-bridge[all]
```

## Quick Start

### FastAPI

```python
from fastapi import FastAPI
from agent_state_bridge.fastapi import create_agent_router

async def my_agent(message: str, state: dict) -> str:
    """Your agent logic here"""
    cart_items = state.get("cart", {}).get("items", [])
    return f"You have {len(cart_items)} items. You said: {message}"

app = FastAPI()
router = create_agent_router(my_agent, tags=["agent"])
app.include_router(router)
```

### Flask

```python
from flask import Flask
from agent_state_bridge.flask import create_agent_blueprint

def my_agent(message: str, state: dict) -> str:
    return f"Processed: {message}"

app = Flask(__name__)
bp = create_agent_blueprint(my_agent)
app.register_blueprint(bp)
```

### Django REST Framework

```python
from agent_state_bridge.django import agent_api_view

@agent_api_view
def my_agent(message: str, state: dict) -> str:
    return f"Processed: {message}"

# In urls.py:
# path('chat/', my_agent)
```

## Integration with AI Frameworks

### LangChain

```python
from langchain_openai import ChatOpenAI
from agent_state_bridge.fastapi import create_agent_router

llm = ChatOpenAI(model="gpt-4o-mini")

async def langchain_agent(message: str, state: dict) -> str:
    response = await llm.ainvoke([{"role": "user", "content": message}])
    return response.content

router = create_agent_router(langchain_agent)
```

### Microsoft Agent Framework

```python
from azure.ai.projects import AIProjectClient
from agent_state_bridge.fastapi import create_agent_router

client = AIProjectClient(...)
agent = client.agents.create_agent(model="gpt-4o-mini")

async def agent_handler(message: str, state: dict) -> str:
    # Your Agent Framework logic
    return response

router = create_agent_router(agent_handler)
```

See `/examples` folder for complete examples with LangChain, Agent Framework, and more.

## API Reference

### Models

- `AgentRequest`: Request model with `message` and `state` fields
- `AgentResponse`: Response model with `response` field

### FastAPI

- `create_agent_router(handler, prefix="", tags=[])`: Create router with `/chat` endpoint
- `AgentBridge`: Class-based approach with decorator

### Flask

- `create_agent_blueprint(handler, name="agent", url_prefix="")`: Create blueprint
- `@agent_route`: Decorator for route handlers

### Django

- `@agent_api_view`: Decorator for function-based views
- `AgentAPIView`: Base class for class-based views

## Frontend Integration

This package works seamlessly with the npm package `agent-state-bridge` for React:

```bash
npm install agent-state-bridge
```

## License

MIT
