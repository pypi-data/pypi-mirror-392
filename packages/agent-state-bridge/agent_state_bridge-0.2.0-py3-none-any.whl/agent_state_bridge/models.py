"""Base models for agent state bridge"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class Action(BaseModel):
    """Action model for state mutations"""
    type: str = Field(..., description="Action type: 'get', 'post', 'put', 'delete', or custom")
    payload: Optional[Dict[str, Any]] = Field(None, description="Action payload data")


class AgentRequest(BaseModel):
    """
    Request model for agent chat endpoint.
    
    Separates concerns:
    - messages: Conversation history
    - actions: State mutations (CRUD operations)
    - context: Application state and RAG data
    """
    messages: List[Message] = Field(..., description="Conversation history")
    actions: List[Action] = Field(default_factory=list, description="Recent actions/mutations")
    context: Dict[str, Any] = Field(default_factory=dict, description="Application state and RAG context")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {"role": "user", "content": "Add product to cart"}
                ],
                "actions": [
                    {"type": "post", "payload": {"item": "product-123"}}
                ],
                "context": {
                    "cart": {"items": [], "total": 0},
                    "products": [{"id": "product-123", "name": "Item"}]
                }
            }
        }
    }


class AgentResponse(BaseModel):
    """Response model for agent chat endpoint"""
    response: str = Field(..., description="Agent response message")
    actions: Optional[List[Action]] = Field(None, description="Actions to execute (optional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Updated context (optional)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "I've added the product to your cart!",
                "actions": [{"type": "post", "payload": {"item": "product-123"}}],
                "context": {"cart": {"items": [{"id": "product-123"}], "total": 29.99}}
            }
        }
    }
