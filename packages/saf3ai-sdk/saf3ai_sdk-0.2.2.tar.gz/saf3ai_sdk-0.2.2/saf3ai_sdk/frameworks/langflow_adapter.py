"""
LangFlow framework adapter.

LangFlow is a visual interface built on top of LangChain, so it can leverage
LangChain's instrumentation. This adapter provides LangFlow-specific integration.
"""

import logging
from typing import Optional, Callable

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class LangFlowFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for LangFlow.
    
    Since LangFlow is built on LangChain, it can use LangChain's callback system.
    This adapter provides LangFlow-specific integration points.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        
        callback = create_framework_security_callbacks(
            framework='langflow',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-langflow-agent-abc123'
        )
        
        # LangFlow uses LangChain under the hood, so LangChain callbacks work
        # The callback can be added to LangFlow components that support callbacks
        ```
    """
    
    def get_framework_name(self) -> str:
        return "langflow"
    
    def create_prompt_callback(self):
        """
        Create LangFlow/LangChain callback for prompt scanning.
        
        Since LangFlow uses LangChain, we can use LangChain's callback system.
        
        Returns:
            LangChain-compatible BaseCallbackHandler instance
        """
        try:
            # Import LangChain callback (LangFlow uses LangChain)
            from saf3ai_sdk.frameworks.langchain import LangChainFrameworkAdapter
            
            # Create LangChain adapter instance and use its callback
            langchain_adapter = LangChainFrameworkAdapter(
                api_endpoint=self.api_endpoint,
                agent_identifier=self.agent_identifier,
                api_key=self.api_key,
                timeout=self.timeout,
                on_scan_complete=self.on_scan_complete
            )
            
            return langchain_adapter.create_prompt_callback()
        
        except ImportError:
            logger.warning("LangChain not available - LangFlow adapter requires LangChain")
            return None
    
    def create_response_callback(self):
        """
        Create LangFlow/LangChain callback for response scanning.
        
        Returns:
            LangChain-compatible BaseCallbackHandler instance
        """
        try:
            # Import LangChain callback (LangFlow uses LangChain)
            from saf3ai_sdk.frameworks.langchain import LangChainFrameworkAdapter
            
            # Create LangChain adapter instance and use its callback
            langchain_adapter = LangChainFrameworkAdapter(
                api_endpoint=self.api_endpoint,
                agent_identifier=self.agent_identifier,
                api_key=self.api_key,
                timeout=self.timeout,
                on_scan_complete=self.on_scan_complete
            )
            
            return langchain_adapter.create_response_callback()
        
        except ImportError:
            logger.warning("LangChain not available - LangFlow adapter requires LangChain")
            return None

