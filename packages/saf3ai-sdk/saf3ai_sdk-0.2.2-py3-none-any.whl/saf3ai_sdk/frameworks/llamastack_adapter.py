"""
Llama Stack framework adapter.

Llama Stack is Meta's ecosystem for Llama models. This adapter provides
security scanning integration for Llama Stack components.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class LlamaStackFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Llama Stack.
    
    Integrates security scanning with Llama Stack components.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='llamastack',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-llamastack-agent-abc123'
        )
        
        # Llama Stack components can use callbacks
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "llamastack"
    
    def create_prompt_callback(self):
        """
        Create Llama Stack callback for prompt scanning.
        
        Returns:
            Callback function that can be used with Llama Stack components
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def llamastack_prompt_callback(prompt: str, **kwargs: Any) -> str:
                """Callback to scan prompts before Llama Stack component execution."""
                try:
                    if prompt:
                        metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                        scan_results = scan_prompt(
                            prompt=str(prompt),
                            api_endpoint=adapter_self.api_endpoint,
                            api_key=adapter_self.api_key,
                            timeout=adapter_self.timeout,
                            metadata=metadata
                        )
                        
                        # Call user callback if provided
                        if adapter_self.on_scan_complete:
                            should_allow = adapter_self.on_scan_complete(str(prompt), scan_results, "prompt")
                            if not should_allow:
                                raise ValueError("Security policy blocked this Llama Stack request")
                    
                    return prompt
                
                except Exception as e:
                    logger.error(f"Llama Stack security scan error: {e}")
                    # Fail open by default
                    return prompt
            
            return llamastack_prompt_callback
        
        except ImportError:
            logger.warning("Llama Stack scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Llama Stack callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def llamastack_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after Llama Stack component execution."""
                try:
                    # Extract response content
                    response_text = ""
                    if isinstance(response, str):
                        response_text = response
                    elif isinstance(response, dict):
                        response_text = response.get('text', response.get('content', str(response)))
                    elif hasattr(response, 'text'):
                        response_text = str(response.text)
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
                                logger.warning("Llama Stack response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"Llama Stack response scan error: {e}")
                    return response
            
            return llamastack_response_callback
        
        except ImportError:
            logger.warning("Llama Stack scanner not available - adapter unavailable")
            return None
