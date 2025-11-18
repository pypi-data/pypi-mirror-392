"""
MultiOn framework adapter.

MultiOn is a browser automation framework. This adapter provides security
scanning integration for MultiOn agent interactions.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class MultiOnFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for MultiOn.
    
    Integrates security scanning with MultiOn agent interactions.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='multion',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-multion-agent-abc123'
        )
        
        # MultiOn agents can use callbacks for action processing
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "multion"
    
    def create_prompt_callback(self):
        """
        Create MultiOn callback for prompt/action scanning.
        
        Returns:
            Callback function that can be used with MultiOn agents
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def multion_prompt_callback(action: Any, **kwargs: Any) -> Any:
                """Callback to scan actions/prompts before MultiOn agent execution."""
                try:
                    # Extract action/prompt content
                    prompt_text = ""
                    if isinstance(action, str):
                        prompt_text = action
                    elif isinstance(action, dict):
                        prompt_text = action.get('prompt', action.get('action', str(action)))
                    elif hasattr(action, 'prompt'):
                        prompt_text = str(action.prompt)
                    elif hasattr(action, 'action'):
                        prompt_text = str(action.action)
                    else:
                        prompt_text = str(action)
                    
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
                                raise ValueError("Security policy blocked this MultiOn action")
                    
                    return action
                
                except Exception as e:
                    logger.error(f"MultiOn security scan error: {e}")
                    # Fail open by default
                    return action
            
            return multion_prompt_callback
        
        except ImportError:
            logger.warning("MultiOn scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create MultiOn callback for response scanning.
        
        Returns:
            Callback function for scanning agent responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def multion_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after MultiOn agent execution."""
                try:
                    # Extract response content
                    response_text = ""
                    if isinstance(response, str):
                        response_text = response
                    elif isinstance(response, dict):
                        response_text = response.get('result', response.get('content', str(response)))
                    elif hasattr(response, 'result'):
                        response_text = str(response.result)
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
                                logger.warning("MultiOn response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"MultiOn response scan error: {e}")
                    return response
            
            return multion_response_callback
        
        except ImportError:
            logger.warning("MultiOn scanner not available - adapter unavailable")
            return None
