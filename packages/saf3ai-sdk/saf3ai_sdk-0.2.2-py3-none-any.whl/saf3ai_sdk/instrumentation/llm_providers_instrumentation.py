"""
Auto-instrumentation for LLM provider SDKs (Cohere, Mistral, Groq, Ollama, xAI).

This module automatically patches provider client classes to add Saf3AI telemetry
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


def _patch_cohere(tracer):
    """Patch Cohere client generate method."""
    try:
        import cohere
        
        if hasattr(cohere.Client, '_saf3ai_instrumented'):
            logger.debug("Cohere Client already instrumented.")
            return True
        
        original_generate = cohere.Client.generate
        
        @functools.wraps(original_generate)
        def instrumented_generate(self, *args, **kwargs):
            """Instrumented Cohere.generate with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_generate(self, *args, **kwargs)
            
            span_name = "cohere.generate"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                prompt = kwargs.get('prompt', args[0] if args else '')
                if prompt:
                    span.set_attribute("cohere.prompt", str(prompt))  # Full prompt
                
                try:
                    result = original_generate(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'generations') and result.generations:
                        response_text = " ".join([gen.text for gen in result.generations if hasattr(gen, 'text')])
                        if response_text:
                            span.set_attribute("cohere.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        cohere.Client.generate = instrumented_generate
        cohere.Client._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented Cohere")
        return True
    
    except ImportError:
        logger.warning("Cohere not found. Skipping Cohere instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument Cohere: {e}")
        return False


def _patch_mistral(tracer):
    """Patch Mistral chat completions."""
    try:
        from mistralai import Mistral
        from mistralai.resources import chat
        
        if hasattr(chat.Chat, '_saf3ai_instrumented'):
            logger.debug("Mistral Chat already instrumented.")
            return True
        
        original_create = chat.Chat.create
        
        @functools.wraps(original_create)
        def instrumented_create(self, *args, **kwargs):
            """Instrumented Mistral Chat.create with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_create(self, *args, **kwargs)
            
            span_name = "mistral.chat.create"
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
                        span.set_attribute("mistral.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("mistral.model", kwargs['model'])
                
                try:
                    result = original_create(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'choices') and result.choices:
                        response_text = result.choices[0].message.content if hasattr(result.choices[0].message, 'content') else ""
                        if response_text:
                            span.set_attribute("mistral.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        chat.Chat.create = instrumented_create
        chat.Chat._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented Mistral")
        return True
    
    except ImportError:
        logger.warning("Mistral not found. Skipping Mistral instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument Mistral: {e}")
        return False


def _patch_groq(tracer):
    """Patch Groq chat completions."""
    try:
        from groq import Groq
        from groq.resources import chat
        
        if hasattr(chat.Completions, '_saf3ai_instrumented'):
            logger.debug("Groq ChatCompletions already instrumented.")
            return True
        
        original_create = chat.Completions.create
        
        @functools.wraps(original_create)
        def instrumented_create(self, *args, **kwargs):
            """Instrumented Groq ChatCompletions.create with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_create(self, *args, **kwargs)
            
            span_name = "groq.chat.completions.create"
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
                        span.set_attribute("groq.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("groq.model", kwargs['model'])
                
                try:
                    result = original_create(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'choices') and result.choices:
                        response_text = result.choices[0].message.content if hasattr(result.choices[0].message, 'content') else ""
                        if response_text:
                            span.set_attribute("groq.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        chat.Completions.create = instrumented_create
        chat.Completions._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented Groq")
        return True
    
    except ImportError:
        logger.warning("Groq not found. Skipping Groq instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument Groq: {e}")
        return False


def _patch_ollama(tracer):
    """Patch Ollama chat and generate methods."""
    try:
        import ollama
        
        if hasattr(ollama, '_saf3ai_instrumented'):
            logger.debug("Ollama already instrumented.")
            return True
        
        original_chat = ollama.chat
        original_generate = ollama.generate
        
        @functools.wraps(original_chat)
        def instrumented_chat(*args, **kwargs):
            """Instrumented ollama.chat with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_chat(*args, **kwargs)
            
            span_name = "ollama.chat"
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
                        span.set_attribute("ollama.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("ollama.model", kwargs['model'])
                
                try:
                    result = original_chat(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'message') and hasattr(result.message, 'content'):
                        response_text = result.message.content
                        if response_text:
                            span.set_attribute("ollama.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        @functools.wraps(original_generate)
        def instrumented_generate(*args, **kwargs):
            """Instrumented ollama.generate with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_generate(*args, **kwargs)
            
            span_name = "ollama.generate"
            with tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                prompt = kwargs.get('prompt', args[0] if args else '')
                if prompt:
                    span.set_attribute("ollama.prompt", str(prompt))  # Full prompt
                
                try:
                    result = original_generate(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'response'):
                        response_text = result.response
                        if response_text:
                            span.set_attribute("ollama.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        ollama.chat = instrumented_chat
        ollama.generate = instrumented_generate
        ollama._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented Ollama")
        return True
    
    except ImportError:
        logger.warning("Ollama not found. Skipping Ollama instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument Ollama: {e}")
        return False


def _patch_xai(tracer):
    """Patch xAI chat completions."""
    try:
        from xai import Grok
        from xai.resources import chat
        
        if hasattr(chat.Completions, '_saf3ai_instrumented'):
            logger.debug("xAI ChatCompletions already instrumented.")
            return True
        
        original_create = chat.Completions.create
        
        @functools.wraps(original_create)
        def instrumented_create(self, *args, **kwargs):
            """Instrumented xAI ChatCompletions.create with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_create(self, *args, **kwargs)
            
            span_name = "xai.chat.completions.create"
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
                        span.set_attribute("xai.prompt", prompt_text)  # Full prompt
                
                if 'model' in kwargs:
                    span.set_attribute("xai.model", kwargs['model'])
                
                try:
                    result = original_create(self, *args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    
                    if hasattr(result, 'choices') and result.choices:
                        response_text = result.choices[0].message.content if hasattr(result.choices[0].message, 'content') else ""
                        if response_text:
                            span.set_attribute("xai.response", response_text)  # Full response
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        chat.Completions.create = instrumented_create
        chat.Completions._saf3ai_instrumented = True
        logger.info("✅ Successfully instrumented xAI")
        return True
    
    except ImportError:
        logger.warning("xAI not found. Skipping xAI instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument xAI: {e}")
        return False


def instrument_cohere(tracer, config=None):
    """Auto-instrument Cohere."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting Cohere auto-instrumentation...")
    result = _patch_cohere(tracer)
    logger.info(f"🎯 Cohere auto-instrumentation complete: {result}")
    return {"cohere_instrumentation": result}


def instrument_mistral(tracer, config=None):
    """Auto-instrument Mistral."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting Mistral auto-instrumentation...")
    result = _patch_mistral(tracer)
    logger.info(f"🎯 Mistral auto-instrumentation complete: {result}")
    return {"mistral_instrumentation": result}


def instrument_groq(tracer, config=None):
    """Auto-instrument Groq."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting Groq auto-instrumentation...")
    result = _patch_groq(tracer)
    logger.info(f"🎯 Groq auto-instrumentation complete: {result}")
    return {"groq_instrumentation": result}


def instrument_ollama(tracer, config=None):
    """Auto-instrument Ollama."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting Ollama auto-instrumentation...")
    result = _patch_ollama(tracer)
    logger.info(f"🎯 Ollama auto-instrumentation complete: {result}")
    return {"ollama_instrumentation": result}


def instrument_xai(tracer, config=None):
    """Auto-instrument xAI."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting xAI auto-instrumentation...")
    result = _patch_xai(tracer)
    logger.info(f"🎯 xAI auto-instrumentation complete: {result}")
    return {"xai_instrumentation": result}

