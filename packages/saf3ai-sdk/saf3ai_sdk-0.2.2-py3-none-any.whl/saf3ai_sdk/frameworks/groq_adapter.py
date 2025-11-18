"""
Groq framework adapter.

This adapter provides security scanning integration for Groq's Python SDK.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class GroqFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Groq.
    
    Integrates security scanning with Groq API calls using client hooks.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from groq import Groq
        
        callback = create_framework_security_callbacks(
            framework='groq',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-groq-agent-abc123'
        )
        
        client = Groq()
        # Callback will be applied via instrumentation
        response = client.chat.completions.create(...)
        ```
    """
    
    def get_framework_name(self) -> str:
        return "groq"
    
    def create_prompt_callback(self):
        """
        Create Groq callback for prompt scanning.
        
        Returns:
            Callback function that can be used with Groq client hooks
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def groq_prompt_callback(request: Dict[str, Any], **kwargs: Any) -> None:
                """Callback to scan prompts before Groq API calls."""
                try:
                    # Extract prompt from request
                    prompt_text = ""
                    if 'messages' in request:
                        # Chat completion format
                        messages = request.get('messages', [])
                        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
                        prompt_text = " ".join(user_messages)
                    elif 'prompt' in request:
                        # Completion format
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
                                raise ValueError("Security policy blocked this Groq request")
                
                except Exception as e:
                    logger.error(f"Groq security scan error: {e}")
                    # Fail open by default
            
            return groq_prompt_callback
        
        except ImportError:
            logger.warning("Groq scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Groq callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def groq_response_callback(response: Any, **kwargs: Any) -> None:
                """Callback to scan responses after Groq API calls."""
                try:
                    # Extract response text
                    response_text = ""
                    if hasattr(response, 'choices') and response.choices:
                        # Chat completion response
                        response_text = response.choices[0].message.content if hasattr(response.choices[0].message, 'content') else str(response.choices[0])
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
                                logger.warning("Groq response blocked by security policy")
                
                except Exception as e:
                    logger.error(f"Groq response scan error: {e}")
            
            return groq_response_callback
        
        except ImportError:
            logger.warning("Groq scanner not available - adapter unavailable")
            return None
