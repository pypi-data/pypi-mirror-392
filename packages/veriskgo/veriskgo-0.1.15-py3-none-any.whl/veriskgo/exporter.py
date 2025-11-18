# src/veriskgo/exporter.py

import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

_DEFAULT_ENDPOINT = "http://localhost:4318/v1/traces"

_provider_initialized = False


def init_otlp_exporter(endpoint: str | None = None, service_name: str = "veriskgo-sdk"):
    """
    Initializes the OTEL tracer provider.
    Safe to call multiple times — only first call takes effect.
    """
    global _provider_initialized
    if _provider_initialized:
        return trace.get_tracer(service_name)

    endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", _DEFAULT_ENDPOINT)

    provider = TracerProvider(
        resource=Resource.create({
            "service.name": service_name,
        })
    )

    exporter = OTLPSpanExporter(endpoint=endpoint)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    _provider_initialized = True

    return trace.get_tracer(service_name)
