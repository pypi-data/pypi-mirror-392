"""
LiteLLM framework adapter.

LiteLLM is a unified interface for multiple LLM providers, so it can leverage
the underlying provider's callback system or use LiteLLM's own hooks.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class LiteLLMFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for LiteLLM.
    
    LiteLLM provides a unified interface, so we can use its callback system
    or delegate to the underlying provider's adapter.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        import litellm
        
        callback = create_framework_security_callbacks(
            framework='litellm',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-litellm-agent-abc123'
        )
        
        # LiteLLM supports callbacks via success_callback and failure_callback
        response = litellm.completion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            # Callbacks can be added via instrumentation
        )
        ```
    """
    
    def get_framework_name(self) -> str:
        return "litellm"
    
    def create_prompt_callback(self):
        """
        Create LiteLLM callback for prompt scanning.
        
        Returns:
            Callback function that can be used with LiteLLM hooks
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def litellm_prompt_callback(kwargs: Dict[str, Any], **extra: Any) -> None:
                """Callback to scan prompts before LiteLLM API calls."""
                try:
                    # Extract prompt from kwargs
                    prompt_text = ""
                    if 'messages' in kwargs:
                        # Chat format
                        messages = kwargs.get('messages', [])
                        user_messages = [msg.get('content', '') for msg in messages if isinstance(msg, dict) and msg.get('role') == 'user']
                        prompt_text = " ".join(user_messages)
                    elif 'prompt' in kwargs:
                        # Completion format
                        prompt_text = str(kwargs.get('prompt', ''))
                    
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
                                raise ValueError("Security policy blocked this LiteLLM request")
                
                except Exception as e:
                    logger.error(f"LiteLLM security scan error: {e}")
                    # Fail open by default
            
            return litellm_prompt_callback
        
        except ImportError:
            logger.warning("LiteLLM scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create LiteLLM callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def litellm_response_callback(kwargs: Dict[str, Any], response: Any, **extra: Any) -> None:
                """Callback to scan responses after LiteLLM API calls."""
                try:
                    # Extract response text
                    response_text = ""
                    if hasattr(response, 'choices') and response.choices:
                        # Chat completion response
                        choice = response.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            response_text = choice.message.content
                        elif hasattr(choice, 'text'):
                            response_text = choice.text
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
                                logger.warning("LiteLLM response blocked by security policy")
                
                except Exception as e:
                    logger.error(f"LiteLLM response scan error: {e}")
            
            return litellm_response_callback
        
        except ImportError:
            logger.warning("LiteLLM scanner not available - adapter unavailable")
            return None
