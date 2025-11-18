"""
Camel AI framework adapter.

Camel AI is a research framework for multi-agent systems. This adapter provides
security scanning integration for Camel AI agent interactions.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class CamelAIFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Camel AI.
    
    Integrates security scanning with Camel AI agent interactions.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='camelai',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-camelai-agent-abc123'
        )
        
        # Camel AI agents can use callbacks for message processing
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "camelai"
    
    def create_prompt_callback(self):
        """
        Create Camel AI callback for prompt/message scanning.
        
        Returns:
            Callback function that can be used with Camel AI agents
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def camelai_prompt_callback(message: Any, **kwargs: Any) -> Any:
                """Callback to scan messages before Camel AI agent processing."""
                try:
                    # Extract message content
                    prompt_text = ""
                    if isinstance(message, str):
                        prompt_text = message
                    elif isinstance(message, dict):
                        prompt_text = message.get('content', str(message))
                    elif hasattr(message, 'content'):
                        prompt_text = str(message.content)
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
                                raise ValueError("Security policy blocked this Camel AI message")
                    
                    return message
                
                except Exception as e:
                    logger.error(f"Camel AI security scan error: {e}")
                    # Fail open by default
                    return message
            
            return camelai_prompt_callback
        
        except ImportError:
            logger.warning("Camel AI scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Camel AI callback for response scanning.
        
        Returns:
            Callback function for scanning agent responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def camelai_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after Camel AI agent processing."""
                try:
                    # Extract response content
                    response_text = ""
                    if isinstance(response, str):
                        response_text = response
                    elif isinstance(response, dict):
                        response_text = response.get('content', str(response))
                    elif hasattr(response, 'content'):
                        response_text = str(response.content)
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
                                logger.warning("Camel AI response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"Camel AI response scan error: {e}")
                    return response
            
            return camelai_response_callback
        
        except ImportError:
            logger.warning("Camel AI scanner not available - adapter unavailable")
            return None
