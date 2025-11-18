"""
agent-state-bridge: Python backend utilities for sharing app state with AI agents
"""

__version__ = "0.2.0"

from .models import AgentRequest, AgentResponse, Message, Action

__all__ = ["AgentRequest", "AgentResponse", "Message", "Action"]
