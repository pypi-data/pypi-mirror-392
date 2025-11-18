"""
Auto-instrumentation for LangChain chains and LLMs.

This module automatically patches LangChain classes to add Saf3AI telemetry
(OpenTelemetry spans and attributes) without requiring manual callback attachment.

Note: Security scanning is optional and handled separately via callbacks
(e.g., create_framework_security_callbacks()).
"""

import functools
import logging
from typing import Any, Dict, Optional, List
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from saf3ai_sdk.logging import logger
from saf3ai_sdk.core.tracer import tracer as saf3ai_tracer_core

# Global storage for SDK config
_sdk_config = None


def _patch_llm_chain(tracer):
    """
    Patch LangChain LLMChain to automatically add Saf3AI callbacks.
    
    This patches the __call__ method to wrap execution with telemetry spans.
    """
    try:
        from langchain.chains import LLMChain
        
        if hasattr(LLMChain, '_saf3ai_instrumented_chain'):
            logger.debug("LLMChain already instrumented.")
            return True
        
        original_call = LLMChain.__call__
        
        @functools.wraps(original_call)
        def instrumented_call(self, inputs: Any, return_only_outputs: bool = False, **kwargs: Any):
            """Instrumented LLMChain.__call__ with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_call(self, inputs, return_only_outputs=return_only_outputs, **kwargs)
            
            otel_tracer = tracer
            span_name = f"langchain.chain.{self.__class__.__name__}"
            
            with otel_tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                # Add chain metadata
                span.set_attribute("langchain.chain.type", self.__class__.__name__)
                if hasattr(self, 'llm') and hasattr(self.llm, 'model_name'):
                    span.set_attribute("langchain.llm.model", str(self.llm.model_name))
                if hasattr(self, 'prompt') and hasattr(self.prompt, 'template'):
                    span.set_attribute("langchain.prompt.template", str(self.prompt.template))  # Full template
                
                # Extract input text for scanning
                input_text = str(inputs) if inputs else ""
                if isinstance(inputs, dict):
                    # Try to get the main input text
                    input_text = inputs.get('input', inputs.get('query', str(inputs)))
                
                span.set_attribute("langchain.input", str(input_text))  # Full input
                
                try:
                    result = original_call(self, inputs, return_only_outputs=return_only_outputs, **kwargs)
                    
                    # Extract output text
                    output_text = str(result) if result else ""
                    if isinstance(result, dict):
                        output_text = result.get('output', result.get('text', str(result)))
                    
                    span.set_attribute("langchain.output", str(output_text))  # Full output
                    span.set_status(Status(StatusCode.OK))
                    
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        
        setattr(LLMChain, '__call__', instrumented_call)
        setattr(LLMChain, '_saf3ai_instrumented_chain', True)
        logger.info("✅ Successfully instrumented LLMChain")
        return True
        
    except ImportError:
        logger.warning("langchain.chains.LLMChain not found. Skipping LLMChain instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument LLMChain: {e}")
        return False


def _patch_base_llm(tracer):
    """
    Patch LangChain BaseLLM to automatically add telemetry.
    
    This patches the _call and _generate methods to capture LLM calls.
    """
    try:
        from langchain.llms.base import BaseLLM
        
        if hasattr(BaseLLM, '_saf3ai_instrumented_llm'):
            logger.debug("BaseLLM already instrumented.")
            return True
        
        original_generate = BaseLLM.generate
        original_agenerate = None
        if hasattr(BaseLLM, 'agenerate'):
            original_agenerate = BaseLLM.agenerate
        
        @functools.wraps(original_generate)
        def instrumented_generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any):
            """Instrumented BaseLLM.generate with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_generate(self, prompts, stop=stop, **kwargs)
            
            otel_tracer = tracer
            span_name = f"langchain.llm.{self.__class__.__name__}.generate"
            
            with otel_tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                # Add LLM metadata
                span.set_attribute("langchain.llm.type", self.__class__.__name__)
                if hasattr(self, 'model_name'):
                    span.set_attribute("langchain.llm.model", str(self.model_name))
                if hasattr(self, 'temperature'):
                    span.set_attribute("langchain.llm.temperature", float(self.temperature))
                
                # Add prompt information
                if prompts:
                    combined_prompt = " ".join(prompts)
                    span.set_attribute("langchain.prompt", str(combined_prompt))  # Full prompt
                    span.set_attribute("langchain.prompt_count", len(prompts))
                
                try:
                    result = original_generate(self, prompts, stop=stop, **kwargs)
                    
                    # Add generation metadata
                    if hasattr(result, 'generations') and result.generations:
                        generation_texts = []
                        for gen_list in result.generations:
                            for gen in gen_list:
                                if hasattr(gen, 'text'):
                                    generation_texts.append(gen.text)
                        
                        if generation_texts:
                            combined_output = " ".join(generation_texts)
                            span.set_attribute("langchain.output", str(combined_output))  # Full output
                            span.set_attribute("langchain.generation_count", len(generation_texts))
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    raise
        
        setattr(BaseLLM, 'generate', instrumented_generate)
        
        # Patch async generate if available
        if original_agenerate:
            @functools.wraps(original_agenerate)
            async def instrumented_agenerate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any):
                """Instrumented BaseLLM.agenerate with telemetry."""
                if not saf3ai_tracer_core.initialized:
                    return await original_agenerate(self, prompts, stop=stop, **kwargs)
                
                otel_tracer = tracer
                span_name = f"langchain.llm.{self.__class__.__name__}.agenerate"
                
                with otel_tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("langchain.llm.type", self.__class__.__name__)
                    if hasattr(self, 'model_name'):
                        span.set_attribute("langchain.llm.model", str(self.model_name))
                    if prompts:
                        combined_prompt = " ".join(prompts)
                        span.set_attribute("langchain.prompt", str(combined_prompt))  # Full prompt
                    
                    try:
                        result = await original_agenerate(self, prompts, stop=stop, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.set_attribute("error.message", str(e))
                        raise
            
            setattr(BaseLLM, 'agenerate', instrumented_agenerate)
        
        setattr(BaseLLM, '_saf3ai_instrumented_llm', True)
        logger.info("✅ Successfully instrumented BaseLLM")
        return True
        
    except ImportError:
        logger.warning("langchain.llms.base.BaseLLM not found. Skipping BaseLLM instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument BaseLLM: {e}")
        return False


def _patch_chat_models(tracer):
    """
    Patch LangChain ChatModels to automatically add telemetry.
    
    This patches ChatOpenAI, ChatAnthropic, etc. to capture chat model calls.
    """
    try:
        from langchain.chat_models.base import BaseChatModel
        
        if hasattr(BaseChatModel, '_saf3ai_instrumented_chat'):
            logger.debug("BaseChatModel already instrumented.")
            return True
        
        original_generate = BaseChatModel.generate
        original_agenerate = None
        if hasattr(BaseChatModel, 'agenerate'):
            original_agenerate = BaseChatModel.agenerate
        
        @functools.wraps(original_generate)
        def instrumented_generate(self, messages: List[Any], stop: Optional[List[str]] = None, **kwargs: Any):
            """Instrumented BaseChatModel.generate with telemetry."""
            if not saf3ai_tracer_core.initialized:
                return original_generate(self, messages, stop=stop, **kwargs)
            
            otel_tracer = tracer
            span_name = f"langchain.chat.{self.__class__.__name__}.generate"
            
            with otel_tracer.start_as_current_span(span_name) as span:
                # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                for key, value in custom_attrs.items():
                    span.set_attribute(key, value)
                
                span.set_attribute("langchain.chat.type", self.__class__.__name__)
                if hasattr(self, 'model_name'):
                    span.set_attribute("langchain.chat.model", str(self.model_name))
                
                # Extract messages
                if messages:
                    message_texts = []
                    for msg in messages:
                        if hasattr(msg, 'content'):
                            message_texts.append(str(msg.content))
                        elif isinstance(msg, dict):
                            message_texts.append(str(msg.get('content', '')))
                    
                    if message_texts:
                        combined_messages = " ".join(message_texts)
                        span.set_attribute("langchain.messages", str(combined_messages))  # Full messages
                        span.set_attribute("langchain.message_count", len(messages))
                
                try:
                    result = original_generate(self, messages, stop=stop, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    raise
        
        setattr(BaseChatModel, 'generate', instrumented_generate)
        
        if original_agenerate:
            @functools.wraps(original_agenerate)
            async def instrumented_agenerate(self, messages: List[Any], stop: Optional[List[str]] = None, **kwargs: Any):
                """Instrumented BaseChatModel.agenerate with telemetry."""
                if not saf3ai_tracer_core.initialized:
                    return await original_agenerate(self, messages, stop=stop, **kwargs)
                
                otel_tracer = tracer
                span_name = f"langchain.chat.{self.__class__.__name__}.agenerate"
                
                with otel_tracer.start_as_current_span(span_name) as span:
                    # Add custom attributes (includes agent_id, framework, and any user-set attributes)
                    custom_attrs = saf3ai_tracer_core.get_custom_attributes()
                    for key, value in custom_attrs.items():
                        span.set_attribute(key, value)
                    
                    span.set_attribute("langchain.chat.type", self.__class__.__name__)
                    if hasattr(self, 'model_name'):
                        span.set_attribute("langchain.chat.model", str(self.model_name))
                    
                    try:
                        result = await original_agenerate(self, messages, stop=stop, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(Status(StatusCode.ERROR, str(e)))
                        span.set_attribute("error.message", str(e))
                        raise
            
            setattr(BaseChatModel, 'agenerate', instrumented_agenerate)
        
        setattr(BaseChatModel, '_saf3ai_instrumented_chat', True)
        logger.info("✅ Successfully instrumented BaseChatModel")
        return True
        
    except ImportError:
        logger.warning("langchain.chat_models.base.BaseChatModel not found. Skipping ChatModel instrumentation.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to instrument BaseChatModel: {e}")
        return False


def instrument_langchain(tracer, config=None):
    """
    Auto-instrument LangChain chains and LLMs. Ensures patches are applied only once.
    
    Args:
        tracer: The OTel Tracer instance (from saf3ai_tracer_core.get_tracer())
        config: Optional SDK Config instance (for error_severity_map access)
    """
    global _sdk_config
    
    # Store config globally for error categorization
    if config:
        _sdk_config = config
        logger.debug("Stored SDK config for LangChain instrumentation")
    
    results = {
        "chain_instrumentation": False,
        "llm_instrumentation": False,
        "chat_model_instrumentation": False,
    }
    
    logger.info("🔧 Starting LangChain auto-instrumentation...")
    
    results["chain_instrumentation"] = _patch_llm_chain(tracer)
    results["llm_instrumentation"] = _patch_base_llm(tracer)
    results["chat_model_instrumentation"] = _patch_chat_models(tracer)
    
    logger.info(f"🎯 LangChain auto-instrumentation complete: {results}")
    return results

