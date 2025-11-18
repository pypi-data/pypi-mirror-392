"""
Auto-instrumentation for Anthropic SDK.

This module automatically patches Anthropic client classes to add Saf3AI telemetry
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


def _patch_anthropic_messages(tracer):
    """Patch Anthropic Messages.create and create_stream methods."""
    try:
        from anthropic import Anthropic
        from anthropic.resources import Messages
        
        if hasattr(Messages, '_saf3ai_instrumented'):
            logger.debug("Anthropic Messages already instrumented.")
            return True
        
        original_create = Messages.create
        original_create_stream = Messages.create_stream
        
        @functools.wraps(original_create)
        def instrumented_create(self, *args, **kwargs):
            """Instrumented Messages.create with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_create(self, *args, **kwargs)
            
            span_name = "anthropic.messages.create"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                # Extract prompt from messages
                messages = kwargs.get('messages', args[0] if args else [])
                if messages:
                    user_messages = [msg.get('content', '') for msg in messages if isinstance(msg, dict) and msg.get('role') == 'user']
                    prompt_text = " ".join(user_messages)
                    if prompt_text:
                        span.set_attribute("anthropic.prompt", prompt_text)  # Full prompt
                
                # Add model info
                if 'model' in kwargs:
                    span.set_attribute("anthropic.model", kwargs['model'])
                
                try:
                    result = original_create(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    # Extract response
                    if hasattr(result, 'content') and result.content:
                        if isinstance(result.content, list):
                            text_parts = [item.text for item in result.content if hasattr(item, 'text')]
                            response_text = " ".join(text_parts)
                        else:
                            response_text = str(result.content)
                        if response_text:
                            span.set_attribute("anthropic.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        @functools.wraps(original_create_stream)
        def instrumented_create_stream(self, *args, **kwargs):
            """Instrumented Messages.create_stream with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_create_stream(self, *args, **kwargs)
            
            span_name = "anthropic.messages.create_stream"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                messages = kwargs.get('messages', args[0] if args else [])
                if messages:
                    user_messages = [msg.get('content', '') for msg in messages if isinstance(msg, dict) and msg.get('role') == 'user']
                    prompt_text = " ".join(user_messages)
                    if prompt_text:
                        span.set_attribute("anthropic.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("anthropic.model", kwargs['model'])
                
                try:
                    # For streaming, we'll mark the span as OK when stream starts
                    span.set_status(Status(StatusCode.OK))
                    return original_create_stream(self, *args, **kwargs)
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        Messages.create = instrumented_create
        Messages.create_stream = instrumented_create_stream
        Messages._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented Anthropic Messages")
        return True
    
    except ImportError:
        logger.warning("Anthropic not found. Skipping Anthropic instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument Anthropic: {e}")
        return False


def instrument_anthropic(tracer, config=None):
    """
    Auto-instrument Anthropic SDK. Ensures patches are applied only once.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance
    """
    global _sdk_config
    
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for Anthropic instrumentation")
    
    results = {
        "messages_instrumentation": False,
    }
    
    logger.info("🔧 Starting Anthropic auto-instrumentation...")
    
    results["messages_instrumentation"] = _patch_anthropic_messages(tracer)
    
    logger.info(f"🎯 Anthropic auto-instrumentation complete: {results}")
    return results

