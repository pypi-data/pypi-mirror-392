"""Saf3AI SDK instrumentation modules."""

from .adk_instrumentation import instrument_adk

__all__ = ["instrument_adk"]

# Lazy imports for all instrumentation modules
try:
    from .langchain_instrumentation import instrument_langchain
    __all__.append("instrument_langchain")
except ImportError:
    pass

try:
    from .openai_instrumentation import instrument_openai
    __all__.append("instrument_openai")
except ImportError:
    pass

try:
    from .anthropic_instrumentation import instrument_anthropic
    __all__.append("instrument_anthropic")
except ImportError:
    pass

try:
    from .llamaindex_instrumentation import instrument_llamaindex
    __all__.append("instrument_llamaindex")
except ImportError:
    pass

try:
    from .llm_providers_instrumentation import (
        instrument_cohere,
        instrument_mistral,
        instrument_groq,
        instrument_ollama,
        instrument_xai
    )
    __all__.extend(["instrument_cohere", "instrument_mistral", "instrument_groq", "instrument_ollama", "instrument_xai"])
except ImportError:
    pass

try:
    from .litellm_instrumentation import instrument_litellm
    __all__.append("instrument_litellm")
except ImportError:
    pass

try:
    from .crewai_instrumentation import instrument_crewai
    __all__.append("instrument_crewai")
except ImportError:
    pass

try:
    from .remaining_frameworks_instrumentation import (
        instrument_ai21,
        instrument_ag2,
        instrument_camelai,
        instrument_haystack,
        instrument_llamastack,
        instrument_multion,
        instrument_smolagents,
        instrument_swarmzero,
        instrument_taskweaver,
        instrument_rest
    )
    __all__.extend([
        "instrument_ai21",
        "instrument_ag2",
        "instrument_camelai",
        "instrument_haystack",
        "instrument_llamastack",
        "instrument_multion",
        "instrument_smolagents",
        "instrument_swarmzero",
        "instrument_taskweaver",
        "instrument_rest"
    ])
except ImportError:
    pass
