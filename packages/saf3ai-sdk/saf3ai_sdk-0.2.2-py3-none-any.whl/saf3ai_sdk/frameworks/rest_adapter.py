"""
REST API generic adapter.

This adapter provides a generic REST API integration for any HTTP-based LLM API.
It can be used as a fallback for frameworks not explicitly supported.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class RESTAPIFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for generic REST API.
    
    Provides a generic callback system for any HTTP-based LLM API.
    This is useful for custom APIs or frameworks not explicitly supported.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='rest',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-rest-api-agent-abc123'
        )
        
        # Use callbacks with your custom REST API client
        # The callbacks provide scan_prompt and scan_response functions
        ```
    """
    
    def get_framework_name(self) -> str:
        return "rest"
    
    def create_prompt_callback(self):
        """
        Create generic REST API callback for prompt scanning.
        
        Returns:
            Callback function that can be used with any REST API client
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def rest_prompt_callback(prompt: str, **kwargs: Any) -> Dict[str, Any]:
                """
                Generic callback to scan prompts before REST API calls.
                
                Args:
                    prompt: The prompt text to scan
                    **kwargs: Additional request parameters
                
                Returns:
                    Scan results dictionary
                """
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
                                raise ValueError("Security policy blocked this REST API request")
                        
                        return scan_results
                
                except Exception as e:
                    logger.error(f"REST API security scan error: {e}")
                    # Fail open by default
                    return {}
            
            return rest_prompt_callback
        
        except ImportError:
            logger.warning("REST API scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create generic REST API callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def rest_response_callback(response: str, **kwargs: Any) -> Dict[str, Any]:
                """
                Generic callback to scan responses after REST API calls.
                
                Args:
                    response: The response text to scan
                    **kwargs: Additional response parameters
                
                Returns:
                    Scan results dictionary
                """
                try:
                    if response:
                        metadata = {"agent_identifier": adapter_self.agent_identifier} if adapter_self.agent_identifier else {}
                        scan_results = scan_response(
                            response=str(response),
                            api_endpoint=adapter_self.api_endpoint,
                            api_key=adapter_self.api_key,
                            timeout=adapter_self.timeout,
                            metadata=metadata
                        )
                        
                        # Call user callback if provided
                        if adapter_self.on_scan_complete:
                            should_allow = adapter_self.on_scan_complete(str(response), scan_results, "response")
                            if not should_allow:
                                logger.warning("REST API response blocked by security policy")
                        
                        return scan_results
                
                except Exception as e:
                    logger.error(f"REST API response scan error: {e}")
                    return {}
            
            return rest_response_callback
        
        except ImportError:
            logger.warning("REST API scanner not available - adapter unavailable")
            return None
