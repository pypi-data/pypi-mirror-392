"""
Cohere framework adapter.

This adapter provides security scanning integration for Cohere's Python SDK.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class CohereFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Cohere.
    
    Integrates security scanning with Cohere API calls using client hooks.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        import cohere
        
        callback = create_framework_security_callbacks(
            framework='cohere',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-cohere-agent-abc123'
        )
        
        client = cohere.Client()
        # Callback will be applied via instrumentation
        response = client.generate(...)
        ```
    """
    
    def get_framework_name(self) -> str:
        return "cohere"
    
    def create_prompt_callback(self):
        """
        Create Cohere callback for prompt scanning.
        
        Returns:
            Callback function that can be used with Cohere client hooks
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def cohere_prompt_callback(request: Dict[str, Any], **kwargs: Any) -> None:
                """Callback to scan prompts before Cohere API calls."""
                try:
                    # Extract prompt from request
                    prompt_text = ""
                    if 'prompt' in request:
                        prompt_text = str(request.get('prompt', ''))
                    elif 'message' in request:
                        prompt_text = str(request.get('message', ''))
                    elif 'prompts' in request:
                        prompts = request.get('prompts', [])
                        prompt_text = " ".join([str(p) for p in prompts])
                    
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
                                raise ValueError("Security policy blocked this Cohere request")
                
                except Exception as e:
                    logger.error(f"Cohere security scan error: {e}")
                    # Fail open by default
            
            return cohere_prompt_callback
        
        except ImportError:
            logger.warning("Cohere scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Cohere callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def cohere_response_callback(response: Any, **kwargs: Any) -> None:
                """Callback to scan responses after Cohere API calls."""
                try:
                    # Extract response text
                    response_text = ""
                    if hasattr(response, 'generations') and response.generations:
                        # Generate response format
                        response_text = " ".join([gen.text for gen in response.generations if hasattr(gen, 'text')])
                    elif hasattr(response, 'text'):
                        response_text = response.text
                    elif isinstance(response, str):
                        response_text = response
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
                                logger.warning("Cohere response blocked by security policy")
                
                except Exception as e:
                    logger.error(f"Cohere response scan error: {e}")
            
            return cohere_response_callback
        
        except ImportError:
            logger.warning("Cohere scanner not available - adapter unavailable")
            return None
