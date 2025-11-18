"""
Auto-instrumentation for OpenAI SDK.

This module automatically patches OpenAI client classes to add Saf3AI telemetry
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


def _patch_openai_chat_completions(tracer):
    """Patch OpenAI ChatCompletion.create and acreate methods."""
    try:
        from openai import OpenAI
        from openai.resources.chat import completions
        
        if hasattr(completions.Completions, '_saf3ai_instrumented'):
            logger.debug("OpenAI ChatCompletions already instrumented.")
            return True
        
        original_create = completions.Completions.create
        original_acreate = completions.Completions.acreate
        
        @functools.wraps(original_create)
        def instrumented_create(self, *args, **kwargs):
            """Instrumented ChatCompletion.create with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_create(self, *args, **kwargs)
            
            span_name = "openai.chat.completions.create"
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
                        span.set_attribute("openai.prompt", prompt_text)  # Full prompt
                
                # Add model info
                if 'model' in kwargs:
                    span.set_attribute("openai.model", kwargs['model'])
                
                try:
                    result = original_create(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    # Extract response
                    if hasattr(result, 'choices') and result.choices:
                        response_text = result.choices[0].message.content if hasattr(result.choices[0].message, 'content') else ""
                        if response_text:
                            span.set_attribute("openai.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        @functools.wraps(original_acreate)
        async def instrumented_acreate(self, *args, **kwargs):
            """Instrumented ChatCompletion.acreate with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return await original_acreate(self, *args, **kwargs)
            
            span_name = "openai.chat.completions.acreate"
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
                        span.set_attribute("openai.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("openai.model", kwargs['model'])
                
                try:
                    result = await original_acreate(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'choices') and result.choices:
                        response_text = result.choices[0].message.content if hasattr(result.choices[0].message, 'content') else ""
                        if response_text:
                            span.set_attribute("openai.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        completions.Completions.create = instrumented_create
        completions.Completions.acreate = instrumented_acreate
        completions.Completions._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented OpenAI ChatCompletions")
        return True
    
    except ImportError:
        logger.warning("OpenAI not found. Skipping OpenAI instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument OpenAI: {e}")
        return False


def instrument_openai(tracer, config=None):
    """
    Auto-instrument OpenAI SDK. Ensures patches are applied only once.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance
    """
    global _sdk_config
    
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for OpenAI instrumentation")
    
    results = {
        "chat_completions_instrumentation": False,
    }
    
    logger.info("🔧 Starting OpenAI auto-instrumentation...")
    
    results["chat_completions_instrumentation"] = _patch_openai_chat_completions(tracer)
    
    logger.info(f"🎯 OpenAI auto-instrumentation complete: {results}")
    return results

