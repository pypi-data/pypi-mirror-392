"""
Ollama framework adapter.

This adapter provides security scanning integration for Ollama (local LLM server).
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class OllamaFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for Ollama.
    
    Integrates security scanning with Ollama API calls.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        import ollama
        
        callback = create_framework_security_callbacks(
            framework='ollama',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-ollama-agent-abc123'
        )
        
        # Callback will be applied via instrumentation
        response = ollama.chat(...)
        ```
    """
    
    def get_framework_name(self) -> str:
        return "ollama"
    
    def create_prompt_callback(self):
        """
        Create Ollama callback for prompt scanning.
        
        Returns:
            Callback function that can be used with Ollama client hooks
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def ollama_prompt_callback(request: Dict[str, Any], **kwargs: Any) -> None:
                """Callback to scan prompts before Ollama API calls."""
                try:
                    # Extract prompt from request
                    prompt_text = ""
                    if 'messages' in request:
                        # Chat format
                        messages = request.get('messages', [])
                        user_messages = [msg.get('content', '') for msg in messages if msg.get('role') == 'user']
                        prompt_text = " ".join(user_messages)
                    elif 'prompt' in request:
                        # Generate format
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
                                raise ValueError("Security policy blocked this Ollama request")
                
                except Exception as e:
                    logger.error(f"Ollama security scan error: {e}")
                    # Fail open by default
            
            return ollama_prompt_callback
        
        except ImportError:
            logger.warning("Ollama scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create Ollama callback for response scanning.
        
        Returns:
            Callback function for scanning responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def ollama_response_callback(response: Any, **kwargs: Any) -> None:
                """Callback to scan responses after Ollama API calls."""
                try:
                    # Extract response text
                    response_text = ""
                    if hasattr(response, 'message') and hasattr(response.message, 'content'):
                        # Chat response format
                        response_text = response.message.content
                    elif hasattr(response, 'response'):
                        # Generate response format
                        response_text = response.response
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
                                logger.warning("Ollama response blocked by security policy")
                
                except Exception as e:
                    logger.error(f"Ollama response scan error: {e}")
            
            return ollama_response_callback
        
        except ImportError:
            logger.warning("Ollama scanner not available - adapter unavailable")
            return None
