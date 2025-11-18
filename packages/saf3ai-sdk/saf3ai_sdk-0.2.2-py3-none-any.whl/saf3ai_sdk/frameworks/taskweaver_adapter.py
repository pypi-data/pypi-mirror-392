"""
TaskWeaver framework adapter.

TaskWeaver is a code-first agent framework. This adapter provides security
scanning integration for TaskWeaver agent interactions.
"""

import logging
from typing import Optional, Callable, Any, Dict

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class TaskWeaverFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for TaskWeaver.
    
    Integrates security scanning with TaskWeaver agent interactions.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='taskweaver',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-taskweaver-agent-abc123'
        )
        
        # TaskWeaver agents can use callbacks for task processing
        # Callbacks can be added via instrumentation
        ```
    """
    
    def get_framework_name(self) -> str:
        return "taskweaver"
    
    def create_prompt_callback(self):
        """
        Create TaskWeaver callback for prompt/task scanning.
        
        Returns:
            Callback function that can be used with TaskWeaver agents
        """
        try:
            from saf3ai_sdk.scanner import scan_prompt
            
            adapter_self = self
            
            def taskweaver_prompt_callback(task: Any, **kwargs: Any) -> Any:
                """Callback to scan tasks/prompts before TaskWeaver agent processing."""
                try:
                    # Extract task/prompt content
                    prompt_text = ""
                    if isinstance(task, str):
                        prompt_text = task
                    elif isinstance(task, dict):
                        prompt_text = task.get('prompt', task.get('task', task.get('content', str(task))))
                    elif hasattr(task, 'prompt'):
                        prompt_text = str(task.prompt)
                    elif hasattr(task, 'task'):
                        prompt_text = str(task.task)
                    elif hasattr(task, 'content'):
                        prompt_text = str(task.content)
                    else:
                        prompt_text = str(task)
                    
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
                                raise ValueError("Security policy blocked this TaskWeaver task")
                    
                    return task
                
                except Exception as e:
                    logger.error(f"TaskWeaver security scan error: {e}")
                    # Fail open by default
                    return task
            
            return taskweaver_prompt_callback
        
        except ImportError:
            logger.warning("TaskWeaver scanner not available - adapter unavailable")
            return None
    
    def create_response_callback(self):
        """
        Create TaskWeaver callback for response scanning.
        
        Returns:
            Callback function for scanning agent responses
        """
        try:
            from saf3ai_sdk.scanner import scan_response
            
            adapter_self = self
            
            def taskweaver_response_callback(response: Any, **kwargs: Any) -> Any:
                """Callback to scan responses after TaskWeaver agent processing."""
                try:
                    # Extract response content
                    response_text = ""
                    if isinstance(response, str):
                        response_text = response
                    elif isinstance(response, dict):
                        response_text = response.get('result', response.get('content', response.get('output', str(response))))
                    elif hasattr(response, 'result'):
                        response_text = str(response.result)
                    elif hasattr(response, 'content'):
                        response_text = str(response.content)
                    elif hasattr(response, 'output'):
                        response_text = str(response.output)
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
                                logger.warning("TaskWeaver response blocked by security policy")
                    
                    return response
                
                except Exception as e:
                    logger.error(f"TaskWeaver response scan error: {e}")
                    return response
            
            return taskweaver_response_callback
        
        except ImportError:
            logger.warning("TaskWeaver scanner not available - adapter unavailable")
            return None
