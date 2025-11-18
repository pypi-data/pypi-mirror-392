# src/veriskgo/__init__.py

"""
VeriskGO Observability SDK

Public API exposed to GenAI applications.
"""

from .tracer import (
    start_trace,
    start_span,
    end_span,
    end_trace,
    current_trace_id,
)

__all__ = [
    "start_trace",
    "start_span",
    "end_span",
    "end_trace",
    "current_trace_id",
]
