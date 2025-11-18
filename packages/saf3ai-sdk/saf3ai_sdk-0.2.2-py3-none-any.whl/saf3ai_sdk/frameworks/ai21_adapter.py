"""
AI21 framework adapter.

This adapter provides security scanning integration for AI21's Python SDK.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class AI21FrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for AI21.
    
    Integrates security scanning with AI21 API calls using client hooks.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from ai21 import AI21Client
        
        callback = create_framework_security_callbacks(
            framework='ai21',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-ai21-agent-abc123'
        )
        
        client = AI21Client()
        # Callback will be applied via instrumentation
        response = client.completion.create(...)
        ```
    """
    
    def get_framework_name(self) -> str:
        return "ai21"
    
    def create_prompt_callback(self):
        """
        Create AI21 callback for prompt scanning.
        
        Returns:
            Callback function that can be used with AI21 client hooks
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def ai21_prompt_callback(request: Dict[str, Any], **kwargs: Any) -> None:
                """Callback to scan prompts before AI21 API calls."""
                try:
                    # Extract prompt from request
                    prompt_text = ""
                    if 'prompt' in request:
                        prompt_text = str(request.get('prompt', ''))
                    elif 'messages' in request:
                        messages = request.get('messages', [])
                        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
                        prompt_text = " ".join(user_messages)
                    
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
                                raise ValueError("Security policy blocked this AI21 request")
                
                except Exception as e:
                    logger.error(f"AI21 security scan error: {e}")
                    # Fail open by default
            
            return ai21_prompt_callback
        
        except ImportError:
            logger.warning("AI21 scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create AI21 callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def ai21_response_callback(response: Any, **kwargs: Any) -> None:
                """Callback to scan responses after AI21 API calls."""
                try:
                    # Extract response text
                    response_text = ""
                    if hasattr(response, 'completions') and response.completions:
                        # Completion response format
                        response_text = response.completions[0].data.text if hasattr(response.completions[0].data, 'text') else str(response.completions[0])
                    elif hasattr(response, 'text'):
                        response_text = response.text
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
                                logger.warning("AI21 response blocked by security policy")
                
                except Exception as e:
                    logger.error(f"AI21 response scan error: {e}")
            
            return ai21_response_callback
        
        except ImportError:
            logger.warning("AI21 scanner not available - adapter unavailable")
            return None
