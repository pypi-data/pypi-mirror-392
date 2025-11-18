# src/veriskgo/exporter.py
import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import requests

from .config import get_cfg

_DEFAULT_ENDPOINT = "http://localhost:4318/v1/traces"


def init_otlp_exporter(endpoint: str | None = None, service_name: str = ''):
    """
    Initialize global OTLP exporter using config.py values.
    """
    cfg = get_cfg()

    endpoint =  _DEFAULT_ENDPOINT
    service_name = service_name or cfg.get("project") or "veriskgo-sdk"

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    exporter = OTLPSpanExporter(endpoint=endpoint)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)


def send_to_otel(trace_data: dict) -> bool:
    """
    Sends trace data to the OTEL backend.
    Returns True if successful, False otherwise.
    """
    try:
        # Define the OTEL backend endpoint (OTLP endpoint)
        endpoint = "http://localhost:4318/v1/traces"  # Change this to your OTEL endpoint
        headers = {
            "Content-Type": "application/json"
        }

        # Send trace data as a POST request to the OTEL backend
        response = requests.post(endpoint, json=trace_data, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            print("Trace data successfully sent to OTEL backend.")
            return True
        else:
            print(f"Failed to send data to OTEL backend: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"Error sending trace data to OTEL backend: {e}")
        return False