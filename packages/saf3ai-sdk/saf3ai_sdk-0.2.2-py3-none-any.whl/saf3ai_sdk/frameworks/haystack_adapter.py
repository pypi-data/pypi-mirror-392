"""
Haystack framework adapter.

Haystack is an NLP framework by deepset. This adapter provides security
scanning integration for Haystack pipelines and components.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class HaystackFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Haystack.
    
    Integrates security scanning with Haystack pipelines and LLM components.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from haystack import Pipeline
        
        callback = create_framework_security_callbacks(
            framework='haystack',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-haystack-agent-abc123'
        )
        
        # Haystack pipelines can use callbacks for component execution
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "haystack"
    
    def create_prompt_callback(self):
        """
        Create Haystack callback for prompt scanning.
        
        Returns:
            Callback function that can be used with Haystack components
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def haystack_prompt_callback(query: str, **kwargs: Any) -> str:
                """Callback to scan queries/prompts before Haystack component execution."""
                try:
                    if query:
                        metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                        scan_results = scan_prompt(
                            prompt=str(query),
                            api_endpoint=adapter_self.api_endpoint,
                            api_key=adapter_self.api_key,
                            timeout=adapter_self.timeout,
                            metadata=metadata
                        )
                        
                        # Call user callback if provided
                        if adapter_self.on_scan_complete:
                            should_allow = adapter_self.on_scan_complete(str(query), scan_results, "prompt")
                            if not should_allow:
                                raise ValueError("Security policy blocked this Haystack query")
                    
                    return query
                
                except Exception as e:
                    logger.error(f"Haystack security scan error: {e}")
                    # Fail open by default
                    return query
            
            return haystack_prompt_callback
        
        except ImportError:
            logger.warning("Haystack scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Haystack callback for response scanning.
        
        Returns:
            Callback function for scanning Haystack component outputs
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def haystack_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after Haystack component execution."""
                try:
                    # Extract response content
                    response_text = ""
                    if isinstance(response, str):
                        response_text = response
                    elif isinstance(response, dict):
                        response_text = response.get('answer', response.get('content', str(response)))
                    elif hasattr(response, 'answer'):
                        response_text = str(response.answer)
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
                                logger.warning("Haystack response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"Haystack response scan error: {e}")
                    return response
            
            return haystack_response_callback
        
        except ImportError:
            logger.warning("Haystack scanner not available - adapter unavailable")
            return None
