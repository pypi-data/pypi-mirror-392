"""
Auto-instrumentation for LiteLLM.

This module automatically patches LiteLLM to add Saf3AI telemetry
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


def _patch_litellm_completion(tracer):
    """Patch LiteLLM completion function."""
    try:
        import litellm
        
        if hasattr(litellm, '_saf3ai_instrumented'):
            logger.debug("LiteLLM already instrumented.")
            return True
        
        original_completion = litellm.completion
        original_acompletion = litellm.acompletion
        
        @functools.wraps(original_completion)
        def instrumented_completion(*args, **kwargs):
            """Instrumented litellm.completion with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_completion(*args, **kwargs)
            
            span_name = "litellm.completion"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                # Extract prompt from messages or prompt
                messages = kwargs.get('messages', args[0] if args and isinstance(args[0], list) else [])
                prompt = kwargs.get('prompt', None)
                
                if messages:
                    user_messages = [msg.get('content', '') for msg in messages if isinstance(msg, dict) and msg.get('role') == 'user']
                    prompt_text = " ".join(user_messages)
                elif prompt:
                    prompt_text = str(prompt)
                else:
                    prompt_text = ""
                
                if prompt_text:
                    span.set_attribute("litellm.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("litellm.model", kwargs['model'])
                
                try:
                    result = original_completion(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    # Extract response
                    if hasattr(result, 'choices') and result.choices:
                        choice = result.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            response_text = choice.message.content
                        elif hasattr(choice, 'text'):
                            response_text = choice.text
                        else:
                            response_text = str(choice)
                        if response_text:
                            span.set_attribute("litellm.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        @functools.wraps(original_acompletion)
        async def instrumented_acompletion(*args, **kwargs):
            """Instrumented litellm.acompletion with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return await original_acompletion(*args, **kwargs)
            
            span_name = "litellm.acompletion"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                messages = kwargs.get('messages', args[0] if args and isinstance(args[0], list) else [])
                prompt = kwargs.get('prompt', None)
                
                if messages:
                    user_messages = [msg.get('content', '') for msg in messages if isinstance(msg, dict) and msg.get('role') == 'user']
                    prompt_text = " ".join(user_messages)
                elif prompt:
                    prompt_text = str(prompt)
                else:
                    prompt_text = ""
                
                if prompt_text:
                    span.set_attribute("litellm.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("litellm.model", kwargs['model'])
                
                try:
                    result = await original_acompletion(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'choices') and result.choices:
                        choice = result.choices[0]
                        if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                            response_text = choice.message.content
                        elif hasattr(choice, 'text'):
                            response_text = choice.text
                        else:
                            response_text = str(choice)
                        if response_text:
                            span.set_attribute("litellm.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        litellm.completion = instrumented_completion
        litellm.acompletion = instrumented_acompletion
        litellm._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented LiteLLM")
        return True
    
    except ImportError:
        logger.warning("LiteLLM not found. Skipping LiteLLM instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument LiteLLM: {e}")
        return False


def instrument_litellm(tracer, config=None):
    """
    Auto-instrument LiteLLM. Ensures patches are applied only once.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance
    """
    global _sdk_config
    
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for LiteLLM instrumentation")
    
    results = {
        "completion_instrumentation": False,
    }
    
    logger.info("🔧 Starting LiteLLM auto-instrumentation...")
    
    results["completion_instrumentation"] = _patch_litellm_completion(tracer)
    
    logger.info(f"🎯 LiteLLM auto-instrumentation complete: {results}")
    return results

