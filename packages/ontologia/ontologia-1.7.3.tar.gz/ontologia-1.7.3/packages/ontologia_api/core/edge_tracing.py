from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def setup_tracing() -> None:
    """Conditionally configure OpenTelemetry tracing for the API.

    Enabled with EDGE_TRACING in env. Attempts to configure OTLP exporter.
    Safe no-op if dependencies are missing or configuration fails.
    """
    if os.getenv("EDGE_TRACING", "0") not in {"1", "true", "True"}:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        try:
            # Prefer OTLP HTTP exporter if available
            pass
        except Exception:  # pragma: no cover - fallback to console if unavailable
            otlp_span_exporter = None  # type: ignore

        service_name = os.getenv("EDGE_TRACING_SERVICE", "ontologia-edge-api")
        endpoint = os.getenv("EDGE_OTLP_ENDPOINT", "http://localhost:4318")
        resource = Resource.create({"service.name": service_name})

        provider = TracerProvider(resource=resource)
        if otlp_span_exporter is not None:
            exporter = otlp_span_exporter(endpoint=f"{endpoint}/v1/traces")
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
        else:  # Fallback to console exporter for quick dev visibility
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter

            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)

        # Instrument FastAPI/Requests if available
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            from opentelemetry.instrumentation.requests import RequestsInstrumentor

            FastAPIInstrumentor().instrument()
            RequestsInstrumentor().instrument()
        except Exception:  # pragma: no cover - optional
            logger.warning("OpenTelemetry instrumentation modules not available")

        logger.info("OpenTelemetry tracing initialized")
    except Exception as exc:  # pragma: no cover - safe no-op on failure
        logger.warning("Failed to initialize OpenTelemetry tracing: %s", exc)
