"""Django REST Framework integration for agent-state-bridge"""
from typing import Callable
try:
    from rest_framework.decorators import api_view
    from rest_framework.response import Response
    from rest_framework.views import APIView
    from rest_framework import status
except ImportError:
    raise ImportError("Django REST Framework is required. Install with: pip install agent-state-bridge[django]")


def agent_api_view(handler: Callable[[str, dict], str]):
    """
    Decorator for Django REST Framework function-based views.
    
    Example:
        ```python
        from agent_state_bridge.django import agent_api_view
        
        @agent_api_view
        def my_agent(message: str, state: dict) -> str:
            return f"Processed: {message}"
        
        # In urls.py:
        # path('chat/', my_agent)
        ```
    """
    @api_view(['POST'])
    def wrapper(request):
        message = request.data.get('message', '')
        state_data = request.data.get('state', {})
        
        try:
            response = handler(message, state_data)
            return Response({'response': response})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return wrapper


class AgentAPIView(APIView):
    """
    Class-based view for Django REST Framework.
    
    Override the `process_agent` method to implement your agent logic.
    
    Example:
        ```python
        from agent_state_bridge.django import AgentAPIView
        
        class MyAgentView(AgentAPIView):
            def process_agent(self, message: str, state: dict) -> str:
                return f"Processed: {message}"
        
        # In urls.py:
        # path('chat/', MyAgentView.as_view())
        ```
    """
    
    def process_agent(self, message: str, state: dict) -> str:
        """Override this method to implement agent logic"""
        raise NotImplementedError("Subclasses must implement process_agent method")
    
    def post(self, request):
        """Handle POST request"""
        message = request.data.get('message', '')
        state_data = request.data.get('state', {})
        
        try:
            response = self.process_agent(message, state_data)
            return Response({'response': response})
        except NotImplementedError:
            return Response(
                {'error': 'process_agent method not implemented'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
