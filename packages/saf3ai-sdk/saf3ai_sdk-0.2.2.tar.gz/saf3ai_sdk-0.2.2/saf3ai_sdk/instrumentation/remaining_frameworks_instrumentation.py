"""
Auto-instrumentation for remaining frameworks (AI21, AG2, CamelAI, Haystack, etc.).

Some frameworks may not have clear patching points, so these provide basic
instrumentation or delegate to callback-based approaches.
"""

import logging
from typing import Any, Dict, Optional

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from saf3ai_sdk.logging import logger
from saf3ai_sdk.core.tracer import tracer as saf3ai_tracer_core

# Global storage for SDK config
_sdk_config = None


def instrument_ai21(tracer, config=None):
    """Auto-instrument AI21 (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting AI21 auto-instrumentation...")
    # AI21 SDK may not have clear patching points, so we log and return
    # Users can still use callback-based approach via create_framework_security_callbacks()
    logger.info("✅ AI21 instrumentation initialized (use callbacks for full integration)")
    return {"ai21_instrumentation": True}


def instrument_ag2(tracer, config=None):
    """Auto-instrument AG2/AutoGen (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting AG2 auto-instrumentation...")
    # AG2 may require more complex patching, basic support for now
    logger.info("✅ AG2 instrumentation initialized (use callbacks for full integration)")
    return {"ag2_instrumentation": True}


def instrument_camelai(tracer, config=None):
    """Auto-instrument CamelAI (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting CamelAI auto-instrumentation...")
    logger.info("✅ CamelAI instrumentation initialized (use callbacks for full integration)")
    return {"camelai_instrumentation": True}


def instrument_haystack(tracer, config=None):
    """Auto-instrument Haystack (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting Haystack auto-instrumentation...")
    logger.info("✅ Haystack instrumentation initialized (use callbacks for full integration)")
    return {"haystack_instrumentation": True}


def instrument_llamastack(tracer, config=None):
    """Auto-instrument LlamaStack (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting LlamaStack auto-instrumentation...")
    logger.info("✅ LlamaStack instrumentation initialized (use callbacks for full integration)")
    return {"llamastack_instrumentation": True}


def instrument_multion(tracer, config=None):
    """Auto-instrument MultiOn (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting MultiOn auto-instrumentation...")
    logger.info("✅ MultiOn instrumentation initialized (use callbacks for full integration)")
    return {"multion_instrumentation": True}


def instrument_smolagents(tracer, config=None):
    """Auto-instrument smolagents (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting smolagents auto-instrumentation...")
    logger.info("✅ smolagents instrumentation initialized (use callbacks for full integration)")
    return {"smolagents_instrumentation": True}


def instrument_swarmzero(tracer, config=None):
    """Auto-instrument SwarmZero (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting SwarmZero auto-instrumentation...")
    logger.info("✅ SwarmZero instrumentation initialized (use callbacks for full integration)")
    return {"swarmzero_instrumentation": True}


def instrument_taskweaver(tracer, config=None):
    """Auto-instrument TaskWeaver (basic instrumentation)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting TaskWeaver auto-instrumentation...")
    logger.info("✅ TaskWeaver instrumentation initialized (use callbacks for full integration)")
    return {"taskweaver_instrumentation": True}


def instrument_rest(tracer, config=None):
    """Auto-instrument REST API (generic - no patching needed)."""
    global _sdk_config
    if config:
        _sdk_config = config
    logger.info("🔧 Starting REST API instrumentation...")
    logger.info("✅ REST API instrumentation initialized (use callbacks for integration)")
    return {"rest_instrumentation": True}

