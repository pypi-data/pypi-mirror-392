"""
Auto-instrumentation for LlamaIndex.

This module automatically patches LlamaIndex classes to add Saf3AI telemetry
(OpenTelemetry spans and attributes) without requiring manual callback attachment.

Note: Security scanning is optional and handled separately via callbacks
(e.g., create_framework_security_callbacks()).
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


def _patch_llamaindex_query_engine(tracer):
    """Patch LlamaIndex QueryEngine.query and aquery methods."""
    try:
        from llama_index.core.query_engine import BaseQueryEngine
        
        if hasattr(BaseQueryEngine, '_saf3ai_instrumented'):
            logger.debug("LlamaIndex QueryEngine already instrumented.")
            return True
        
        original_query = BaseQueryEngine.query
        original_aquery = BaseQueryEngine.aquery
        
        @functools.wraps(original_query)
        def instrumented_query(self, str_or_query_bundle, **kwargs):
            """Instrumented QueryEngine.query with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_query(self, str_or_query_bundle, **kwargs)
            
            span_name = "llamaindex.query_engine.query"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                # Extract query text
                query_text = str(str_or_query_bundle) if not hasattr(str_or_query_bundle, 'query_str') else str_or_query_bundle.query_str
                if query_text:
                    span.set_attribute("llamaindex.query", query_text)  # Full query
                
                try:
                    result = original_query(self, str_or_query_bundle, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    # Extract response
                    if hasattr(result, 'response'):
                        response_text = str(result.response)
                        if response_text:
                            span.set_attribute("llamaindex.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        @functools.wraps(original_aquery)
        async def instrumented_aquery(self, str_or_query_bundle, **kwargs):
            """Instrumented QueryEngine.aquery with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return await original_aquery(self, str_or_query_bundle, **kwargs)
            
            span_name = "llamaindex.query_engine.aquery"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                query_text = str(str_or_query_bundle) if not hasattr(str_or_query_bundle, 'query_str') else str_or_query_bundle.query_str
                if query_text:
                    span.set_attribute("llamaindex.query", query_text)  # Full query
                
                try:
                    result = await original_aquery(self, str_or_query_bundle, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'response'):
                        response_text = str(result.response)
                        if response_text:
                            span.set_attribute("llamaindex.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        BaseQueryEngine.query = instrumented_query
        BaseQueryEngine.aquery = instrumented_aquery
        BaseQueryEngine._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented LlamaIndex QueryEngine")
        return True
    
    except ImportError:
        logger.warning("LlamaIndex not found. Skipping LlamaIndex instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument LlamaIndex: {e}")
        return False


def instrument_llamaindex(tracer, config=None):
    """
    Auto-instrument LlamaIndex. Ensures patches are applied only once.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance
    """
    global _sdk_config
    
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for LlamaIndex instrumentation")
    
    results = {
        "query_engine_instrumentation": False,
    }
    
    logger.info("🔧 Starting LlamaIndex auto-instrumentation...")
    
    results["query_engine_instrumentation"] = _patch_llamaindex_query_engine(tracer)
    
    logger.info(f"🎯 LlamaIndex auto-instrumentation complete: {results}")
    return results

