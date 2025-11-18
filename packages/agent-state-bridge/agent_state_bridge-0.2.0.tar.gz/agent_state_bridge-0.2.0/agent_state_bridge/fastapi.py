"""FastAPI integration for agent-state-bridge"""
from typing import Callable, Awaitable, List, Dict, Any
from fastapi import APIRouter
from .models import AgentRequest, AgentResponse, Message, Action


def create_agent_router(
    agent_handler: Callable[[List[Message], List[Action], Dict[str, Any]], Awaitable[AgentResponse]],
    prefix: str = "",
    tags: list[str] = None
) -> APIRouter:
    """
    Create a FastAPI router with agent chat endpoint.
    
    Args:
        agent_handler: Async function that takes (messages, actions, context) 
                      and returns AgentResponse
        prefix: Router prefix (default: "")
        tags: Router tags for OpenAPI docs
        
    Returns:
        FastAPI APIRouter with /chat endpoint
        
    Example:
        ```python
        from fastapi import FastAPI
        from agent_state_bridge.fastapi import create_agent_router
        from agent_state_bridge.models import AgentResponse
        
        async def my_agent(messages, actions, context):
            last_message = messages[-1].content if messages else ""
            # Your agent logic here
            return AgentResponse(response=f"Processed: {last_message}")
        
        app = FastAPI()
        router = create_agent_router(my_agent, tags=["agent"])
        app.include_router(router)
        ```
    """
    router = APIRouter(prefix=prefix, tags=tags or ["agent"])
    
    @router.post("/chat", response_model=AgentResponse)
    async def chat_endpoint(request: AgentRequest) -> AgentResponse:
        """
        Agent chat endpoint.
        
        Accepts:
        - messages: Conversation history
        - actions: Recent state mutations (CRUD operations)
        - context: Application state and RAG data
        
        Returns:
        - response: Agent message
        - actions: Optional actions to execute
        - context: Optional updated context
        """
        return await agent_handler(request.messages, request.actions, request.context)
    
    return router


# Alternative: Decorator-based approach
class AgentBridge:
    """
    Class-based approach for FastAPI integration.
    
    Example:
        ```python
        from fastapi import FastAPI
        from agent_state_bridge.fastapi import AgentBridge
        from agent_state_bridge.models import AgentResponse
        
        app = FastAPI()
        bridge = AgentBridge(app)
        
        @bridge.agent_handler
        async def my_agent(messages, actions, context):
            last_msg = messages[-1].content if messages else ""
            return AgentResponse(response=f"Got: {last_msg}")
        ```
    """
    
    def __init__(self, app=None, prefix: str = "", tags: list[str] = None):
        self.prefix = prefix
        self.tags = tags or ["agent"]
        self._handler = None
        if app:
            self.init_app(app)
    
    def agent_handler(self, func: Callable[[List[Message], List[Action], Dict[str, Any]], Awaitable[AgentResponse]]):
        """Decorator to register agent handler"""
        self._handler = func
        return func
    
    def init_app(self, app):
        """Initialize with FastAPI app"""
        if not self._handler:
            raise ValueError("No agent handler registered. Use @bridge.agent_handler decorator")
        
        router = create_agent_router(self._handler, self.prefix, self.tags)
        app.include_router(router)
