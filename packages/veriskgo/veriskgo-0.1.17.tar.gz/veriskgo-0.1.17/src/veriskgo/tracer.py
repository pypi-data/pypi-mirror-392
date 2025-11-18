# src/veriskgo/tracer.py

from __future__ import annotations
from opentelemetry import trace
import time
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# =========================
# Start a new trace
# =========================
def start_trace(
    name: str,
    metadata: Dict[str, Any] | None = None
) -> str:
    tracer = trace.get_tracer("veriskgo")

    trace_id = str(uuid.uuid4())

    span = tracer.start_span(
        name=name,
        attributes={
            "trace.type": "root",
            "trace.id": trace_id,
            **(metadata or {})
        }
    )

    span.__enter__()  # make it active
    return trace_id


# =========================
# Start child span
# =========================
def start_span(
    name: str,
    input: Optional[str] = None,
    metadata: Dict[str, Any] | None = None
):
    tracer = trace.get_tracer("veriskgo")

    span = tracer.start_span(
        name=name,
        attributes={
            "span.input": input or "",
            **(metadata or {})
        }
    )

    span.__enter__()
    return span


# =========================
# End span
# =========================
def end_span(
    span,
    output: Optional[str] = None,
    usage: Dict[str, Any] | None = None,
    success: bool = True
):
    if span is None:
        return

    if output:
        span.set_attribute("span.output", output)
    if usage:
        for k, v in usage.items():
            span.set_attribute(f"usage.{k}", v)

    span.set_attribute("success", success)

    span.__exit__(None, None, None)


# =========================
# End entire trace
# =========================
def end_trace(
    final_output: Optional[str] = None,
    success: bool = True
):
    span = trace.get_current_span()
    if span:
        if final_output:
            span.set_attribute("trace.output", final_output)
        span.set_attribute("success", success)
        span.__exit__(None, None, None)
