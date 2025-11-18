"""Flask integration for agent-state-bridge"""
from typing import Callable
from functools import wraps
try:
    from flask import request, jsonify, Blueprint
except ImportError:
    raise ImportError("Flask is required. Install with: pip install agent-state-bridge[flask]")


def create_agent_blueprint(
    agent_handler: Callable[[str, dict], str],
    name: str = "agent",
    url_prefix: str = ""
) -> "Blueprint":
    """
    Create a Flask blueprint with agent chat endpoint.
    
    Args:
        agent_handler: Function that takes (message, state) and returns response string
        name: Blueprint name
        url_prefix: URL prefix for the blueprint
        
    Returns:
        Flask Blueprint with /chat endpoint
        
    Example:
        ```python
        from flask import Flask
        from agent_state_bridge.flask import create_agent_blueprint
        
        def my_agent(message: str, state: dict) -> str:
            return f"Processed: {message}"
        
        app = Flask(__name__)
        bp = create_agent_blueprint(my_agent)
        app.register_blueprint(bp)
        ```
    """
    bp = Blueprint(name, __name__, url_prefix=url_prefix)
    
    @bp.route("/chat", methods=["POST"])
    def chat_endpoint():
        """Agent chat endpoint"""
        data = request.get_json()
        message = data.get("message", "")
        state = data.get("state", {})
        
        response = agent_handler(message, state)
        return jsonify({"response": response})
    
    return bp


def agent_route(handler: Callable[[str, dict], str]):
    """
    Decorator for Flask route handlers.
    
    Example:
        ```python
        from flask import Flask
        from agent_state_bridge.flask import agent_route
        
        app = Flask(__name__)
        
        @app.route("/chat", methods=["POST"])
        @agent_route
        def my_agent(message: str, state: dict) -> str:
            return f"Got: {message}"
        ```
    """
    @wraps(handler)
    def wrapper():
        data = request.get_json()
        message = data.get("message", "")
        state = data.get("state", {})
        
        response = handler(message, state)
        return jsonify({"response": response})
    
    return wrapper
