"""Saf3AI SDK main entry point."""

from typing import Optional, Dict, Union, Any, Literal

from saf3ai_sdk.config import Config
from saf3ai_sdk.core.tracer import tracer, TracingCore
from saf3ai_sdk.core.auth import auth_manager
from saf3ai_sdk.logging import logger

# Import decorators for easy access
from saf3ai_sdk.core.decorators import trace, agent, task, tool, workflow

# Import security scanning functionality (consolidated from adk-otel)
from saf3ai_sdk.callbacks import (
    register_security_callback,
    get_callback_manager,
    LLMSecurityCallback,
    LLMCallbackManager
)
# ADK callbacks are imported conditionally when framework="adk" is used
# (see _get_adk_security_callback function below)
from saf3ai_sdk.scanner import scan_prompt, scan_response, scan_prompt_and_response

# Import framework adapters
from saf3ai_sdk.frameworks import BaseFrameworkAdapter, get_framework_adapter

__all__ = [
    "init",
    "tracer",
    "get_tracer",
    "trace",
    "agent",
    "task",
    "tool",
    "workflow",
    "reset_session",
    "set_custom_attributes",  # NEW
    "get_custom_attributes",   # NEW
    "clear_custom_attributes", # NEW
    # Security scanning (from adk-otel, now consolidated)
    "register_security_callback",
    "get_callback_manager",
    "LLMSecurityCallback",
    "LLMCallbackManager",
    "create_security_callback",
    "scan_prompt",
    "scan_response",
    "scan_prompt_and_response",
    # Framework adapters
    "BaseFrameworkAdapter",
    "get_framework_adapter",
    "create_framework_security_callbacks",  # NEW helper
]

def create_security_callback(*args, **kwargs):
    """
    Create ADK security callback for prompt/response scanning.
    
    This is a lazy import wrapper that only imports ADK callbacks when needed.
    Only use this when framework="adk" or "google-adk".
    
    For other frameworks, use create_framework_security_callbacks() instead.
    
    Args:
        *args, **kwargs: Arguments passed to adk_callbacks.create_security_callback
        
    Returns:
        ADK security callback function(s)
        
    Raises:
        ImportError: If ADK is not available and this function is called
    """
    # Lazy import - only import when actually needed
    from saf3ai_sdk.adk_callbacks import create_security_callback as _create_adk_callback
    return _create_adk_callback(*args, **kwargs)


def get_tracer(name: str = "saf3ai"):
    """
    Get a tracer from the Saf3AI SDK's TracerProvider.
    
    This ensures spans are processed by our span processors.
    
    Args:
        name: Name of the tracer
        
    Returns:
        Tracer instance from our TracerProvider
    """
    return tracer.get_tracer(name)


def set_custom_attributes(attributes: Dict[str, Any]) -> None:
    """Set custom attributes to be added to all future spans."""
    tracer.set_custom_attributes(attributes)


def get_custom_attributes() -> Dict[str, Any]:
    """Get current custom attributes."""
    return tracer.get_custom_attributes()


def clear_custom_attributes() -> None:
    """Clear all custom attributes."""
    tracer.clear_custom_attributes()


def init(
    service_name: str,
    framework: Literal[
        'adk', 'google-adk',
        'langchain',
        'langflow',
        'llamaindex', 'llama-index',
        'openai',
        'anthropic',
        'cohere',
        'mistral',
        'groq',
        'ollama',
        'xai', 'x-ai',
        'crewai', 'crew-ai',
        'ag2', 'autogen',
        'camelai', 'camel-ai',
        'ai21',
        'haystack',
        'llamastack', 'llama-stack',
        'litellm',
        'multion',
        'smolagents',
        'swarmzero', 'swarm-zero',
        'taskweaver', 'task-weaver',
        'rest', 'rest-api', 'generic'
    ],
    agent_id: str,
    api_key: str,
    api_key_header_name: str,
    safeai_collector_agent: str,
    environment: Optional[str] = None,
    safeai_collector_headers: Optional[Dict[str, str]] = None,
    log_level: Optional[Union[str, int]] = None,
    debug_mode: Optional[bool] = None,
    console_output: Optional[bool] = None,
    error_severity_map: Optional[Dict[str, str]] = None,  # Custom severity mapping
    auth_enabled: Optional[bool] = None,
    **kwargs
) -> TracingCore:
    """
    Initialize the Saf3AI SDK.
    
    Configures the global tracer, sets up exporters, and applies
    automatic instrumentation for the specified framework.
    
    Args:
        service_name: Name of the service being instrumented (required)
        framework: AI framework being used. Must be one of the supported framework names:
                  'adk', 'google-adk', 'langchain', 'llamaindex', 'llama-index', 'openai', 
                  'anthropic', 'cohere', 'mistral', 'groq', 'ollama', 'xai', 'x-ai',
                  'crewai', 'crew-ai', 'ag2', 'autogen', 'camelai', 'camel-ai', 'ai21',
                  'haystack', 'llamastack', 'llama-stack', 'litellm', 'multion', 'smolagents',
                  'swarmzero', 'swarm-zero', 'taskweaver', 'task-weaver', 'rest', 'rest-api', 'generic'
                  (required, strictly typed - only these values are accepted)
        agent_id: Unique identifier for this agent (alphanumeric, e.g., 'financial-coordinator-b14fd') (required)
        api_key: Organization API key for authentication (required)
        api_key_header_name: HTTP header name used for the API key (e.g., 'X-API-Key') (required)
        safeai_collector_agent: Saf3AI Collector endpoint URL (required)
        environment: Environment name (development, staging, production). Default: 'development'
        safeai_collector_headers: Additional headers for Saf3AI Collector requests (e.g., Authorization)
        log_level: Logging level for Saf3AI SDK (DEBUG, INFO, WARNING, ERROR)
        debug_mode: Enable debug logging
        console_output: Print telemetry to console
        error_severity_map: Custom mapping of error categories to severity levels
                            Default: {'security': 'critical', 'operational': 'warning', 
                                     'user_error': 'info', 'unknown': 'error'}
        auth_enabled: Enable or disable SDK-level authentication
        **kwargs: Additional configuration parameters passed to config.configure()
        
    Returns:
        TracingCore: The initialized tracer instance
        
    Raises:
        ValueError: If any required parameter is missing or empty
    """
    
    # Validate required parameters
    if not service_name or not service_name.strip():
        raise ValueError("'service_name' is required and cannot be empty")
    
    if not framework or not framework.strip():
        raise ValueError("'framework' is required and cannot be empty")
    
    # Validate framework name - must be a supported framework
    framework_lower = framework.lower().strip()
    from saf3ai_sdk.frameworks import list_supported_frameworks
    supported_frameworks = list_supported_frameworks()
    
    if framework_lower not in supported_frameworks:
        raise ValueError(
            f"Unsupported framework: '{framework}'. "
            f"Supported frameworks: {', '.join(sorted(supported_frameworks))}"
        )
    
    if not agent_id or not agent_id.strip():
        raise ValueError("'agent_id' is required and cannot be empty")
    
    if not api_key or not api_key.strip():
        raise ValueError("'api_key' is required and cannot be empty")
    
    if not api_key_header_name or not api_key_header_name.strip():
        raise ValueError("'api_key_header_name' is required and cannot be empty")
    
    if not safeai_collector_agent or not safeai_collector_agent.strip():
        raise ValueError("'safeai_collector_agent' is required and cannot be empty")
    
    config = Config()
    
    config.configure(
        service_name=service_name,
        environment=environment,
        safeai_endpoint=safeai_collector_agent,
        safeai_headers=safeai_collector_headers,
        log_level=log_level,
        debug_mode=debug_mode,
        console_output=console_output,
        error_severity_map=error_severity_map,
        auth_enabled=auth_enabled,
        api_key=api_key,
        api_key_header_name=api_key_header_name,
        **kwargs
    )
    
    # Set initial custom attributes (agent_id, framework) that are always included
    # Users can add more custom attributes later using set_custom_attributes()
    set_custom_attributes({
        'agent_id': agent_id,
        'framework': framework,
        'saf3ai.framework': framework
    })
    
    auth_manager.configure(
        enabled=config.auth_enabled,
        api_key=config.api_key,
        header_name=config.api_key_header_name,
    )

    # Initialize the core tracer
    tracer.initialize(config)
    
    # Apply framework-specific auto-instrumentation based on framework parameter
    framework_lower = framework.lower().strip()
    
    # Framework-specific initialization - only execute code for the selected framework
    if framework_lower in ['adk', 'google-adk']:
        # ADK-specific: Import and apply auto-instrumentation (patches ADK classes)
        try:
            from saf3ai_sdk.instrumentation import instrument_adk
            instrument_adk(tracer.get_tracer("saf3ai-adk"), config)
            logger.info(f"Applied ADK auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"ADK instrumentation not available: {e}. ADK features may not work correctly.")
    elif framework_lower in ['langchain', 'langflow']:
        # LangChain/LangFlow-specific: Import and apply auto-instrumentation (patches LangChain classes)
        # Note: LangFlow uses LangChain under the hood, so LangChain instrumentation works for both
        try:
            from saf3ai_sdk.instrumentation import instrument_langchain
            instrument_langchain(tracer.get_tracer("saf3ai-langchain"), config)
            logger.info(f"Applied LangChain auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"LangChain instrumentation not available: {e}. {framework} features may not work correctly.")
    elif framework_lower == 'openai':
        try:
            from saf3ai_sdk.instrumentation import instrument_openai
            instrument_openai(tracer.get_tracer("saf3ai-openai"), config)
            logger.info(f"Applied OpenAI auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"OpenAI instrumentation not available: {e}. OpenAI features may not work correctly.")
    elif framework_lower == 'anthropic':
        try:
            from saf3ai_sdk.instrumentation import instrument_anthropic
            instrument_anthropic(tracer.get_tracer("saf3ai-anthropic"), config)
            logger.info(f"Applied Anthropic auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"Anthropic instrumentation not available: {e}. Anthropic features may not work correctly.")
    elif framework_lower in ['llamaindex', 'llama-index']:
        try:
            from saf3ai_sdk.instrumentation import instrument_llamaindex
            instrument_llamaindex(tracer.get_tracer("saf3ai-llamaindex"), config)
            logger.info(f"Applied LlamaIndex auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"LlamaIndex instrumentation not available: {e}. LlamaIndex features may not work correctly.")
    elif framework_lower == 'cohere':
        try:
            from saf3ai_sdk.instrumentation import instrument_cohere
            instrument_cohere(tracer.get_tracer("saf3ai-cohere"), config)
            logger.info(f"Applied Cohere auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"Cohere instrumentation not available: {e}. Cohere features may not work correctly.")
    elif framework_lower == 'mistral':
        try:
            from saf3ai_sdk.instrumentation import instrument_mistral
            instrument_mistral(tracer.get_tracer("saf3ai-mistral"), config)
            logger.info(f"Applied Mistral auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"Mistral instrumentation not available: {e}. Mistral features may not work correctly.")
    elif framework_lower == 'groq':
        try:
            from saf3ai_sdk.instrumentation import instrument_groq
            instrument_groq(tracer.get_tracer("saf3ai-groq"), config)
            logger.info(f"Applied Groq auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"Groq instrumentation not available: {e}. Groq features may not work correctly.")
    elif framework_lower == 'ollama':
        try:
            from saf3ai_sdk.instrumentation import instrument_ollama
            instrument_ollama(tracer.get_tracer("saf3ai-ollama"), config)
            logger.info(f"Applied Ollama auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"Ollama instrumentation not available: {e}. Ollama features may not work correctly.")
    elif framework_lower in ['xai', 'x-ai']:
        try:
            from saf3ai_sdk.instrumentation import instrument_xai
            instrument_xai(tracer.get_tracer("saf3ai-xai"), config)
            logger.info(f"Applied xAI auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"xAI instrumentation not available: {e}. xAI features may not work correctly.")
    elif framework_lower == 'litellm':
        try:
            from saf3ai_sdk.instrumentation import instrument_litellm
            instrument_litellm(tracer.get_tracer("saf3ai-litellm"), config)
            logger.info(f"Applied LiteLLM auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"LiteLLM instrumentation not available: {e}. LiteLLM features may not work correctly.")
    elif framework_lower in ['crewai', 'crew-ai']:
        try:
            from saf3ai_sdk.instrumentation import instrument_crewai
            instrument_crewai(tracer.get_tracer("saf3ai-crewai"), config)
            logger.info(f"Applied CrewAI auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"CrewAI instrumentation not available: {e}. CrewAI features may not work correctly.")
    elif framework_lower == 'ai21':
        try:
            from saf3ai_sdk.instrumentation import instrument_ai21
            instrument_ai21(tracer.get_tracer("saf3ai-ai21"), config)
            logger.info(f"Applied AI21 auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"AI21 instrumentation not available: {e}. AI21 features may not work correctly.")
    elif framework_lower in ['ag2', 'autogen']:
        try:
            from saf3ai_sdk.instrumentation import instrument_ag2
            instrument_ag2(tracer.get_tracer("saf3ai-ag2"), config)
            logger.info(f"Applied AG2 auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"AG2 instrumentation not available: {e}. AG2 features may not work correctly.")
    elif framework_lower in ['camelai', 'camel-ai']:
        try:
            from saf3ai_sdk.instrumentation import instrument_camelai
            instrument_camelai(tracer.get_tracer("saf3ai-camelai"), config)
            logger.info(f"Applied CamelAI auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"CamelAI instrumentation not available: {e}. CamelAI features may not work correctly.")
    elif framework_lower == 'haystack':
        try:
            from saf3ai_sdk.instrumentation import instrument_haystack
            instrument_haystack(tracer.get_tracer("saf3ai-haystack"), config)
            logger.info(f"Applied Haystack auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"Haystack instrumentation not available: {e}. Haystack features may not work correctly.")
    elif framework_lower in ['llamastack', 'llama-stack']:
        try:
            from saf3ai_sdk.instrumentation import instrument_llamastack
            instrument_llamastack(tracer.get_tracer("saf3ai-llamastack"), config)
            logger.info(f"Applied LlamaStack auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"LlamaStack instrumentation not available: {e}. LlamaStack features may not work correctly.")
    elif framework_lower == 'multion':
        try:
            from saf3ai_sdk.instrumentation import instrument_multion
            instrument_multion(tracer.get_tracer("saf3ai-multion"), config)
            logger.info(f"Applied MultiOn auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"MultiOn instrumentation not available: {e}. MultiOn features may not work correctly.")
    elif framework_lower == 'smolagents':
        try:
            from saf3ai_sdk.instrumentation import instrument_smolagents
            instrument_smolagents(tracer.get_tracer("saf3ai-smolagents"), config)
            logger.info(f"Applied smolagents auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"smolagents instrumentation not available: {e}. smolagents features may not work correctly.")
    elif framework_lower in ['swarmzero', 'swarm-zero']:
        try:
            from saf3ai_sdk.instrumentation import instrument_swarmzero
            instrument_swarmzero(tracer.get_tracer("saf3ai-swarmzero"), config)
            logger.info(f"Applied SwarmZero auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"SwarmZero instrumentation not available: {e}. SwarmZero features may not work correctly.")
    elif framework_lower in ['taskweaver', 'task-weaver']:
        try:
            from saf3ai_sdk.instrumentation import instrument_taskweaver
            instrument_taskweaver(tracer.get_tracer("saf3ai-taskweaver"), config)
            logger.info(f"Applied TaskWeaver auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"TaskWeaver instrumentation not available: {e}. TaskWeaver features may not work correctly.")
    elif framework_lower in ['rest', 'rest-api', 'generic']:
        try:
            from saf3ai_sdk.instrumentation import instrument_rest
            instrument_rest(tracer.get_tracer("saf3ai-rest"), config)
            logger.info(f"Applied REST API auto-instrumentation for framework: {framework}")
        except ImportError as e:
            logger.warning(f"REST API instrumentation not available: {e}. REST API features may not work correctly.")
    # All frameworks now have auto-instrumentation support
    else:
        logger.warning(f"Framework '{framework}' not recognized. Auto-instrumentation may not be available.")
            
    return tracer

def create_framework_security_callbacks(
    framework: str,
    api_endpoint: str,
    agent_identifier: str,
    api_key: Optional[str] = None,
    timeout: int = 10,
    on_scan_complete: Optional[Any] = None,
    scan_responses: bool = False
):
    """
    Create framework-specific security callbacks.
    
    This is a convenience function that automatically creates the right callbacks
    based on the framework being used.
    
    Args:
        framework: Framework name ('adk', 'langchain', 'llamaindex')
        api_endpoint: URL of the on-prem scanning API
        agent_identifier: Agent identifier for custom guardrails
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds
        on_scan_complete: Optional callback function(text, scan_results, text_type) -> bool
        scan_responses: Whether to also scan responses (framework-dependent)
    
    Returns:
        Framework-specific callback(s) - format depends on framework
    """
    adapter_class = get_framework_adapter(framework)
    
    if not adapter_class:
        logger.error(f"Unknown framework: {framework}. Supported: adk, langchain, llamaindex")
        return None
    
    # Create the adapter instance
    adapter = adapter_class(
        api_endpoint=api_endpoint,
        agent_identifier=agent_identifier,
        api_key=api_key,
        timeout=timeout,
        on_scan_complete=on_scan_complete
    )
    
    # For ADK, use the create_callbacks convenience method
    if framework in ['adk', 'google-adk']:
        return adapter.create_callbacks(scan_responses=scan_responses)
    
    # For other frameworks, return both callbacks
    if scan_responses:
        return (adapter.create_prompt_callback(), adapter.create_response_callback())
    else:
        return adapter.create_prompt_callback()


def reset_session():
    """
    Reset the current persistent session to create a new session.
    Call this when you want to start a new ADK web session.
    This will create a new persistent session ID and clean up old session data.
    """
    try:
        from saf3ai_sdk.instrumentation.adk_instrumentation import reset_persistent_session
        return reset_persistent_session()
    except ImportError:
        print("🔍 DEBUG: ADK instrumentation not available")
        return None

# Alias init_telemetry for compatibility (was init_telemetry in adk-otel)
init_telemetry = init