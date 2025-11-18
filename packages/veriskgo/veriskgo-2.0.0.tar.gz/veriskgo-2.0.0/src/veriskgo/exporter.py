# src/veriskgo/exporter.py
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from .config import get_cfg

_DEFAULT_ENDPOINT = "http://localhost:4318/v1/traces"


def init_otlp_exporter(endpoint: str | None = None, service_name: str = ''):
    """
    Initialize global OTLP exporter using config.py values.
    """
    cfg = get_cfg()

    endpoint = endpoint or cfg.get("langfuse_endpoint") or _DEFAULT_ENDPOINT
    service_name = service_name or cfg.get("project") or "veriskgo-sdk"

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    exporter = OTLPSpanExporter(endpoint=endpoint)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)
