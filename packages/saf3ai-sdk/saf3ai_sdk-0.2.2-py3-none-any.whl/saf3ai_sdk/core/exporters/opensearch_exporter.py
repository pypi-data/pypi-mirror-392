"""Saf3AI Collector exporter for Saf3AI SDK."""

import threading
from typing import Dict, Optional, Sequence
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult

from saf3ai_sdk.logging import logger


class Saf3AIOTLPExporter(OTLPSpanExporter):
    """Custom Saf3AI Collector exporter that sends telemetry data to Saf3AI Collector using HTTP."""
    
    def __init__(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        service_name: str = "saf3ai-agent",
        environment: str = "development",
        **kwargs
    ):
        """
        Initialize the Saf3AI Collector exporter.
        
        Args:
            endpoint: Saf3AI Collector HTTP endpoint (required, should be provided via SDK initialization)
            headers: Additional headers for Saf3AI Collector requests
            service_name: Name of the service being instrumented
            environment: Environment name
            **kwargs: Additional arguments passed to parent exporter
        """
        super().__init__(endpoint=endpoint, headers=headers, **kwargs)
        self.service_name = service_name
        self.environment = environment
        self._lock = threading.Lock()
        
        logger.info(f"Saf3AI Collector exporter initialized for {service_name} ({environment}) → {endpoint}")
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to Saf3AI Collector.
        
        Args:
            spans: Sequence of spans to export
            
        Returns:
            SpanExportResult indicating success or failure
        """
        # REMOVED: Debug print statements - not needed for production
        # Reason: These print statements were for debugging during development.
        # Production code should use logger instead. Keeping logger.debug/error for error tracking.
        if not spans:
            return SpanExportResult.SUCCESS
        
        try:
            # Note: Custom attributes are added during span creation in the tracer
            # No need to modify spans here as they're already properly configured
            
            # Use parent exporter
            result = super().export(spans)
            
            if result == SpanExportResult.SUCCESS:
                logger.debug(f"Successfully exported {len(spans)} spans to Saf3AI Collector")
            else:
                logger.warning(f"Failed to export {len(spans)} spans to Saf3AI Collector")
            
            return result
            
        except Exception as e:
            logger.error(f"Error exporting spans to Saf3AI Collector: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        try:
            # super().shutdown()
            logger.debug("Saf3AI Collector exporter shutdown complete")
        except Exception as e:
            logger.error(f"Error during Saf3AI Collector exporter shutdown: {e}")
