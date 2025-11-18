"""
CrewAI framework adapter.

CrewAI is built on top of LangChain, so it can leverage LangChain's callback system.
This adapter provides CrewAI-specific integration.
"""

import logging
from typing import Optional, Callable

from .base import BaseFrameworkAdapter

logger = logging.getLogger(__name__)


class CrewAIFrameworkAdapter(BaseFrameworkAdapter):
    """
    Framework adapter for CrewAI.
    
    Since CrewAI is built on LangChain, it can use LangChain's callback system.
    This adapter provides CrewAI-specific integration points.
    
    Example Usage:
        ```python
        from saf3ai_sdk import create_framework_security_callbacks
        from crewai import Agent, Task, Crew
        
        callback = create_framework_security_callbacks(
            framework='crewai',
            api_endpoint='http://localhost:8082',
            agent_identifier='my-crewai-agent-abc123'
        )
        
        # CrewAI uses LangChain under the hood, so LangChain callbacks work
        # The callback can be added to CrewAI agents/tasks
        ```
    """
    
    def get_framework_name(self) -> str:
        return "crewai"
    
    def create_prompt_callback(self):
        """
        Create CrewAI/LangChain callback for prompt scanning.
        
        Since CrewAI uses LangChain, we can use LangChain's callback system.
        
        Returns:
            LangChain-compatible BaseCallbackHandler instance
        """
        try:
            # Import LangChain callback (CrewAI uses LangChain)
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
            logger.warning("LangChain not available - CrewAI adapter requires LangChain")
            return None
    
    def create_response_callback(self):
        """
        Create CrewAI/LangChain callback for response scanning.
        
        Returns:
            LangChain-compatible BaseCallbackHandler instance
        """
        try:
            # Import LangChain callback (CrewAI uses LangChain)
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
            logger.warning("LangChain not available - CrewAI adapter requires LangChain")
            return None
