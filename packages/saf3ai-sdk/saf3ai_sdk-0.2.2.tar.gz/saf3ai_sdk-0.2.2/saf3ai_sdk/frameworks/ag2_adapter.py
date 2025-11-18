"""
AG2 (AutoGen) framework adapter.

AG2 (formerly AutoGen) is a multi-agent framework. This adapter provides
security scanning integration for AG2 agent interactions.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class AG2FrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for AG2 (AutoGen).
    
    Integrates security scanning with AG2 agent interactions.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from autogen import ConversableAgent
        
        callback = create_framework_security_callbacks(
            framework='ag2',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-ag2-agent-abc123'
        )
        
        # AG2 agents can use callbacks for message processing
        agent = ConversableAgent(...)
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "ag2"
    
    def create_prompt_callback(self):
        """
        Create AG2 callback for prompt/message scanning.
        
        Returns:
            Callback function that can be used with AG2 agents
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def ag2_prompt_callback(message: Any, **kwargs: Any) -> Any:
                """Callback to scan messages before AG2 agent processing."""
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
                                raise ValueError("Security policy blocked this AG2 message")
                    
                    return message
                
                except Exception as e:
                    logger.error(f"AG2 security scan error: {e}")
                    # Fail open by default
                    return message
            
            return ag2_prompt_callback
        
        except ImportError:
            logger.warning("AG2 scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create AG2 callback for response scanning.
        
        Returns:
            Callback function for scanning agent responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def ag2_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after AG2 agent processing."""
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
                                logger.warning("AG2 response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"AG2 response scan error: {e}")
                    return response
            
            return ag2_response_callback
        
        except ImportError:
            logger.warning("AG2 scanner not available - adapter unavailable")
            return None
