"""
Anthropic framework adapter.

This adapter provides security scanning integration for Anthropic's Python SDK (Claude).
Uses Anthropic's client hooks/callbacks to intercept API calls.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class AnthropicFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Anthropic (Claude).
    
    Integrates security scanning with Anthropic API calls using client hooks.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from anthropic import Anthropic
        
        callback = create_framework_security_callbacks(
            framework='anthropic',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-anthropic-agent-abc123'
        )
        
        client = Anthropic()
        # Callback will be applied via instrumentation
        response = client.messages.create(...)
        ```
    """
    
    def get_framework_name(self) -> str:
        return "anthropic"
    
    def create_prompt_callback(self):
        """
        Create Anthropic callback for prompt scanning.
        
        Returns:
            Callback function that can be used with Anthropic client hooks
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def anthropic_prompt_callback(request: Dict[str, Any], **kwargs: Any) -> None:
                """Callback to scan prompts before Anthropic API calls."""
                try:
                    # Extract prompt from request
                    prompt_text = ""
                    if 'messages' in request:
                        # Messages format
                        messages = request.get('messages', [])
                        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
                        prompt_text = " ".join(user_messages)
                    elif 'prompt' in request:
                        # Legacy prompt format
                        prompt_text = str(request.get('prompt', ''))
                    
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
                                raise ValueError("Security policy blocked this Anthropic request")
                
                except Exception as e:
                    logger.error(f"Anthropic security scan error: {e}")
                    # Fail open by default
            
            return anthropic_prompt_callback
        
        except ImportError:
            logger.warning("Anthropic scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Anthropic callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def anthropic_response_callback(response: Any, **kwargs: Any) -> None:
                """Callback to scan responses after Anthropic API calls."""
                try:
                    # Extract response text
                    response_text = ""
                    if hasattr(response, 'content') and response.content:
                        # Messages response format
                        if isinstance(response.content, list):
                            text_parts = [item.text for item in response.content if hasattr(item, 'text')]
                            response_text = " ".join(text_parts)
                        else:
                            response_text = str(response.content)
                    elif hasattr(response, 'completion'):
                        # Legacy completion format
                        response_text = response.completion
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
                                logger.warning("Anthropic response blocked by security policy")
                
                except Exception as e:
                    logger.error(f"Anthropic response scan error: {e}")
            
            return anthropic_response_callback
        
        except ImportError:
            logger.warning("Anthropic scanner not available - adapter unavailable")
            return None
