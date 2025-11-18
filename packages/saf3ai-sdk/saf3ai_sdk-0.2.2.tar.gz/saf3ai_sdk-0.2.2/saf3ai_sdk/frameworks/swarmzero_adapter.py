"""
SwarmZero framework adapter.

SwarmZero is a multi-agent framework. This adapter provides security
scanning integration for SwarmZero agent interactions.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class SwarmZeroFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for SwarmZero.
    
    Integrates security scanning with SwarmZero agent interactions.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='swarmzero',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-swarmzero-agent-abc123'
        )
        
        # SwarmZero agents can use callbacks for message processing
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "swarmzero"
    
    def create_prompt_callback(self):
        """
        Create SwarmZero callback for prompt/message scanning.
        
        Returns:
            Callback function that can be used with SwarmZero agents
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def swarmzero_prompt_callback(message: Any, **kwargs: Any) -> Any:
                """Callback to scan messages before SwarmZero agent processing."""
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
                                raise ValueError("Security policy blocked this SwarmZero message")
                    
                    return message
                
                except Exception as e:
                    logger.error(f"SwarmZero security scan error: {e}")
                    # Fail open by default
                    return message
            
            return swarmzero_prompt_callback
        
        except ImportError:
            logger.warning("SwarmZero scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create SwarmZero callback for response scanning.
        
        Returns:
            Callback function for scanning agent responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def swarmzero_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after SwarmZero agent processing."""
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
                                logger.warning("SwarmZero response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"SwarmZero response scan error: {e}")
                    return response
            
            return swarmzero_response_callback
        
        except ImportError:
            logger.warning("SwarmZero scanner not available - adapter unavailable")
            return None
