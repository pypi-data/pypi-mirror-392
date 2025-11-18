# src/veriskgo/tracer.py
from __future__ import annotations
import time
import uuid
import threading
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from opentelemetry import trace
from opentelemetry.context import attach, detach, set_value
from .exporter import init_otlp_exporter

_LOCK = threading.Lock()

# data structure to track active trace + open spans
_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],  # list of dicts: {span_id, span_obj, token, start_time}
}

# Tracer singleton (set by init_tracing)
_TRACER = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def init_tracing(endpoint: str | None = None, service_name: str = "veriskgo-sdk"):
    """
    Initialize OTLP exporter + tracer. Call once at app startup.
    """
    global _TRACER
    _TRACER = init_otlp_exporter(endpoint=endpoint, service_name=service_name)
    return _TRACER


def current_trace_id() -> Optional[str]:
    with _LOCK:
        return _ACTIVE_TRACE.get("trace_id")


def start_trace(name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Start a new root trace. Creates root span and sets it as current context.
    Returns trace_id (uuid string).
    """
    global _TRACER
    if _TRACER is None:
        _TRACER = init_tracing()  # fallback init with defaults

    with _LOCK:
        trace_id = _new_id()
        root_span_id = _new_id()

        # start OTEL span object (not using context manager)
        span = _TRACER.start_span(name)
        span.set_attribute("start_time_iso", _now_iso())
        # attach span to current context
        ctx = trace.set_span_in_context(span)
        token = attach(ctx)

        _ACTIVE_TRACE["trace_id"] = trace_id
        _ACTIVE_TRACE["spans"] = [
            {
                "span_id": root_span_id,
                "span_obj": span,
                "token": token,
                "start_time": time.time(),
                "name": name,
                "metadata": dict(metadata or {}),
            }
        ]

        # set metadata attributes on root span
        if metadata:
            for k, v in metadata.items():
                if v is not None:
                    span.set_attribute(k, v)

        return trace_id


def start_span(name: str, input: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Start a child span under the most recent active span.
    Returns a span_id which can be used to end the span later.
    """
    global _TRACER
    if _TRACER is None:
        _TRACER = init_tracing()

    with _LOCK:
        if _ACTIVE_TRACE.get("trace_id") is None:
            raise RuntimeError("No active trace. Call start_trace() first.")

        parent_entry = _ACTIVE_TRACE["spans"][-1]
        parent_ctx = trace.set_span_in_context(parent_entry["span_obj"])

        span_id = _new_id()
        span = _TRACER.start_span(name, context=parent_ctx)
        span.set_attribute("start_time_iso", _now_iso())
        if input is not None:
            # set input as attribute (or use a sanitized attribute key)
            span.set_attribute("gen_ai.prompt", input)
        if metadata:
            for k, v in metadata.items():
                if v is not None:
                    span.set_attribute(k, v)

        token = attach(trace.set_span_in_context(span))

        _ACTIVE_TRACE["spans"].append(
            {
                "span_id": span_id,
                "span_obj": span,
                "token": token,
                "start_time": time.time(),
                "name": name,
                "metadata": dict(metadata or {}),
            }
        )
        return span_id


def end_span(span_id: Optional[str] = None, output: Optional[str] = None, usage: Optional[Dict[str, Any]] = None,
             success: bool = True, error: Optional[str] = None) -> None:
    """
    End the given span (or most recent if span_id is None).
    Updates attributes (output, usage, success) and ends the OTEL span.
    """
    with _LOCK:
        if _ACTIVE_TRACE.get("trace_id") is None:
            return

        if span_id is None:
            entry = _ACTIVE_TRACE["spans"].pop()
        else:
            # find entry by id and pop it
            idx = None
            for i in range(len(_ACTIVE_TRACE["spans"]) - 1, -1, -1):
                if _ACTIVE_TRACE["spans"][i]["span_id"] == span_id:
                    idx = i
                    break
            if idx is None:
                return
            entry = _ACTIVE_TRACE["spans"].pop(idx)

        span = entry["span_obj"]
        token = entry["token"]
        duration_ms = int((time.time() - entry["start_time"]) * 1000)

        # set attributes safely
        if output is not None:
            span.set_attribute("gen_ai.completion", output)
        if usage:
            # attach usage fields as attributes (flattened)
            for k, v in usage.items():
                try:
                    span.set_attribute(f"gen_ai.usage.{k}", v)
                except Exception:
                    span.set_attribute(f"gen_ai.usage.{k}", str(v))
        span.set_attribute("duration_ms", duration_ms)
        span.set_attribute("success", bool(success))
        if error:
            span.set_attribute("error_message", error)

        # end span and detach context
        try:
            span.end()
        finally:
            try:
                detach(token)
            except Exception:
                pass


def end_trace(final_output: Optional[str] = None, success: bool = True) -> Optional[Dict[str, Any]]:
    """
    End all open spans, flush exporter, and return a package (useful for tests).
    """
    with _LOCK:
        if _ACTIVE_TRACE.get("trace_id") is None:
            return None

        # close remaining spans (LIFO)
        while _ACTIVE_TRACE["spans"]:
            end_span()

        trace_id = _ACTIVE_TRACE["trace_id"]
        # Build a minimal bundle for debugging/tests
        bundle = {
            "trace_id": trace_id,
            # we don't keep full span dicts after closing, but you can extend to store them
        }

        # Optionally set final root attributes -- no root span left, so skip
        # Force flush to the OTLP exporter so collector receives spans
        provider = trace.get_tracer_provider()
       

        # Reset internal state
        _ACTIVE_TRACE["trace_id"] = None
        _ACTIVE_TRACE["spans"] = []

        return bundle
