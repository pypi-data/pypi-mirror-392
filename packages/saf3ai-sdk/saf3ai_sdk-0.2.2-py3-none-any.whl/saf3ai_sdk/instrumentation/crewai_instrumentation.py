"""
Auto-instrumentation for CrewAI.

CrewAI uses LangChain under the hood, so we can leverage LangChain instrumentation.
This module ensures CrewAI-specific components are also instrumented.
"""

import functools
import logging
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from saf3ai_sdk.logging import logger
from saf3ai_sdk.core.tracer import tracer as saf3ai_tracer_core

# Global storage for SDK config
_sdk_config = None


def instrument_crewai(tracer, config=None):
    """
    Auto-instrument CrewAI.
    
    Since CrewAI uses LangChain, we apply LangChain instrumentation.
    Additionally, we can patch CrewAI-specific components if needed.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance
    """
    global _sdk_config
    
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for CrewAI instrumentation")
    
    # CrewAI uses LangChain, so apply LangChain instrumentation
    try:
        from saf3ai_sdk.instrumentation import instrument_langchain
        logger.info("🔧 Starting CrewAI auto-instrumentation (using LangChain instrumentation)...")
        result = instrument_langchain(tracer, config)
        logger.info(f"🎯 CrewAI auto-instrumentation complete (via LangChain)")
        return result
    except ImportError:
        logger.warning("LangChain instrumentation not available for CrewAI")
        return {"crewai_instrumentation": False}

