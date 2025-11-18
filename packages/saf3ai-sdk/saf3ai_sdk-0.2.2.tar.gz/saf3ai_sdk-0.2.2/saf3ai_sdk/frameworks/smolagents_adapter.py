"""
smolagents framework adapter.

smolagents is a lightweight agent framework. This adapter provides security
scanning integration for smolagents agent interactions.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class SmolagentsFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for smolagents.
    
    Integrates security scanning with smolagents agent interactions.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='smolagents',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-smolagents-agent-abc123'
        )
        
        # smolagents agents can use callbacks for message processing
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "smolagents"
    
    def create_prompt_callback(self):
        """
        Create smolagents callback for prompt/message scanning.
        
        Returns:
            Callback function that can be used with smolagents agents
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def smolagents_prompt_callback(message: Any, **kwargs: Any) -> Any:
                """Callback to scan messages before smolagents agent processing."""
                try:
                    # Extract message content
                    prompt_text = ""
                    if isinstance(message, str):
                        prompt_text = message
                    elif isinstance(message, dict):
                        prompt_text = message.get('content', message.get('message', str(message)))
                    elif hasattr(message, 'content'):
                        prompt_text = str(message.content)
                    elif hasattr(message, 'message'):
                        prompt_text = str(message.message)
                    else:
                        prompt_text = str(message)
                    
                    if prompt_text:
                        metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                        scan_results = scan_prompt(
                            prompt=prompt_text,
                            api_endpoint=adapter_self.api_endpoint,
                            api_key=adapter_self.api_key,
                            timeout=adapter_self.timeout,
                            metadata=metadata
                        )
                        
                        # Call user callback if provided
                        if adapter_self.on_scan_complete:
                            should_allow = adapter_self.on_scan_complete(prompt_text, scan_results, "prompt")
                            if not should_allow:
                                raise ValueError("Security policy blocked this smolagents message")
                    
                    return message
                
                except Exception as e:
                    logger.error(f"smolagents security scan error: {e}")
                    # Fail open by default
                    return message
            
            return smolagents_prompt_callback
        
        except ImportError:
            logger.warning("smolagents scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create smolagents callback for response scanning.
        
        Returns:
            Callback function for scanning agent responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def smolagents_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after smolagents agent processing."""
                try:
                    # Extract response content
                    response_text = ""
                    if isinstance(response, str):
                        response_text = response
                    elif isinstance(response, dict):
                        response_text = response.get('content', response.get('response', str(response)))
                    elif hasattr(response, 'content'):
                        response_text = str(response.content)
                    elif hasattr(response, 'response'):
                        response_text = str(response.response)
                    else:
                        response_text = str(response)
                    
                    if response_text:
                        metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                        scan_results = scan_response(
                            response=response_text,
                            api_endpoint=adapter_self.api_endpoint,
                            api_key=adapter_self.api_key,
                            timeout=adapter_self.timeout,
                            metadata=metadata
                        )
                        
                        # Call user callback if provided
                        if adapter_self.on_scan_complete:
                            should_allow = adapter_self.on_scan_complete(response_text, scan_results, "response")
                            if not should_allow:
                                logger.warning("smolagents response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"smolagents response scan error: {e}")
                    return response
            
            return smolagents_response_callback
        
        except ImportError:
            logger.warning("smolagents scanner not available - adapter unavailable")
            return None
