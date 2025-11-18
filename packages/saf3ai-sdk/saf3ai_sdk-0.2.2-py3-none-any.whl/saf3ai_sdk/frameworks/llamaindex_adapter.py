"""
LlamaIndex framework adapter.

This adapter provides security scanning integration for LlamaIndex using CallbackManager.
"""

import logging
from typing import Optional, Callable, Any, Dict, List

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class LlamaIndexFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for LlamaIndex.
    
    Integrates security scanning with LlamaIndex using CallbackManager.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from llama_index.core.callbacks import CallbackManager
        
        callback = create_framework_security_callbacks(
            framework='llamaindex',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-llamaindex-agent-abc123'
        )
        
        callback_manager = CallbackManager([callback])
        # Use callback_manager with LlamaIndex components
        ```
    """
    
    def get_framework_name(self) -> str:
        return "llamaindex"
    
    def create_prompt_callback(self):
        """
        Create LlamaIndex callback handler for prompt and response scanning.
        
        Returns:
            LlamaIndex-compatible callback handler instance
        """
        try:
            from llama_index.core.callbacks import BaseCallbackHandler
            from llama_index.core.callbacks.schema import CBEventType, EventPayload
            
            # Import scanner
            from saf3ai_sdk.scanner import scan_prompt, scan_response
            
            adapter_self = self
            
            class Saf3AILlamaIndexCallback(BaseCallbackHandler):
                """LlamaIndex callback handler for Saf3AI security scanning."""
                
                def __init__(self):
                    super().__init__(
                        event_starts_to_ignore=[],
                        event_ends_to_ignore=[],
                    )
                
                def on_event_start(
                    self,
                    event_type: CBEventType,
                    payload: Optional[Dict[str, Any]] = None,
                    event_id: str = "",
                    parent_id: str = "",
                    **kwargs: Any
                ) -> str:
                    """Handle event start - scan prompts before LLM calls."""
                    if event_type == CBEventType.LLM:
                        try:
                            # Extract prompt from payload
                            prompt = None
                            if payload:
                                if EventPayload.PROMPT in payload:
                                    prompt = payload[EventPayload.PROMPT]
                                elif EventPayload.MESSAGES in payload:
                                    messages = payload[EventPayload.MESSAGES]
                                    if messages:
                                        prompt = str(messages[-1].content if hasattr(messages[-1], 'content') else messages[-1])
                            
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
                                        raise ValueError("Security policy blocked this LlamaIndex request")
                        
                        except Exception as e:
                            logger.error(f"LlamaIndex security scan error: {e}")
                            # Fail open by default
                    
                    return event_id
                
                def on_event_end(
                    self,
                    event_type: CBEventType,
                    payload: Optional[Dict[str, Any]] = None,
                    event_id: str = "",
                    **kwargs: Any
                ) -> None:
                    """Handle event end - scan responses after LLM calls."""
                    if event_type == CBEventType.LLM:
                        try:
                            # Extract response from payload
                            response = None
                            if payload:
                                if EventPayload.RESPONSE in payload:
                                    response_obj = payload[EventPayload.RESPONSE]
                                    if hasattr(response_obj, 'message'):
                                        response = response_obj.message.content if hasattr(response_obj.message, 'content') else str(response_obj.message)
                                    elif hasattr(response_obj, 'text'):
                                        response = response_obj.text
                                    else:
                                        response = str(response_obj)
                            
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
                                        logger.warning("LlamaIndex response blocked by security policy")
                        
                        except Exception as e:
                            logger.error(f"LlamaIndex response scan error: {e}")
            
            return Saf3AILlamaIndexCallback()
        
        except ImportError:
            logger.warning("LlamaIndex not installed - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        For LlamaIndex, both prompt and response scanning happen in the same callback handler.
        
        Returns:
            Same as create_prompt_callback()
        """
        return self.create_prompt_callback()
