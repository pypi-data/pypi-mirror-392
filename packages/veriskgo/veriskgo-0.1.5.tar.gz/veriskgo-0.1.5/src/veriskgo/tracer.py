# src/veriskgo/tracer.py
"""
Thread-safe lightweight tracer for GenAI spans.

API:
  start_trace(name, user_id=None, session_id=None, metadata=None) -> trace_id
  start_span(name, input=None, metadata=None) -> span_id
  end_span(span_id=None, output=None, usage=None, success=True, error=None) -> None
  end_trace(final_output=None, success=True) -> bundle
  set_span_input(text) -> None
  set_span_usage(usage_dict) -> None
  current_trace_id() -> Optional[str]
"""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .langfuse import send_bundle, is_enabled
from .config import get_cfg

_LOCK = threading.Lock()

# Active trace container (single-trace per process model; can be extended)
_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],  # list of span dicts (root first)
    "stack": [],  # active open spans: list of {"span_id", "start_time"}
}


# -------------------------
# Helpers
# -------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def current_trace_id() -> Optional[str]:
    with _LOCK:
        return _ACTIVE_TRACE.get("trace_id")


# -------------------------
# Public API
# -------------------------
def start_trace(
    name: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Start a new trace and create a root span. Returns the trace_id.
    If a trace is already active, it will be replaced by the new one.
    """
    with _LOCK:
        trace_id = _new_id()
        root_span_id = _new_id()

        meta = dict(metadata or {})
        if user_id:
            meta.setdefault("user_id", user_id)
        if session_id:
            meta.setdefault("session_id", session_id)

        root_span = {
            "span_id": root_span_id,
            "parent_span_id": None,
            "name": name,
            "operation": "trace.root",
            "type": "root",
            "timestamp": _now_iso(),
            "input": "",
            "output": "",
            "metadata": meta,
            "usage": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE["trace_id"] = trace_id
        _ACTIVE_TRACE["spans"] = [root_span]
        _ACTIVE_TRACE["stack"] = [{"span_id": root_span_id, "start_time": time.time()}]

        return trace_id


def start_span(
    name: str,
    input: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Start a child span under the most recent active span.
    Returns the new span_id.
    """
    with _LOCK:
        if _ACTIVE_TRACE.get("trace_id") is None:
            raise RuntimeError("No active trace. Call start_trace() first.")

        parent_span_id = _ACTIVE_TRACE["stack"][-1]["span_id"] if _ACTIVE_TRACE["stack"] else None
        span_id = _new_id()

        span = {
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "name": name,
            "operation": "span",
            "type": "child",
            "timestamp": _now_iso(),
            "input": input or "",
            "output": "",
            "metadata": dict(metadata or {}),
            "usage": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE["spans"].append(span)
        _ACTIVE_TRACE["stack"].append({"span_id": span_id, "start_time": time.time()})
        return span_id


def end_span(
    span_id: Optional[str] = None,
    output: Optional[str] = None,
    usage: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> None:
    """
    End a span. If span_id is None, ends the most recently opened span.
    Updates output, usage, duration and success/error metadata.
    """
    with _LOCK:
        if not _ACTIVE_TRACE.get("trace_id"):
            return

        # If user didn't pass span_id, pop from stack
        if span_id is None:
            if not _ACTIVE_TRACE["stack"]:
                return
            entry = _ACTIVE_TRACE["stack"].pop()
            span_id_to_close = entry["span_id"]
            duration_ms = int((time.time() - entry["start_time"]) * 1000)
        else:
            # find stack entry for provided span_id (and remove it)
            span_id_to_close = span_id
            duration_ms = None
            # remove matching entry from stack if present
            for i in range(len(_ACTIVE_TRACE["stack"]) - 1, -1, -1):
                if _ACTIVE_TRACE["stack"][i]["span_id"] == span_id:
                    duration_ms = int((time.time() - _ACTIVE_TRACE["stack"][i]["start_time"]) * 1000)
                    _ACTIVE_TRACE["stack"].pop(i)
                    break
            if duration_ms is None:
                # span not found in active stack; compute duration zero
                duration_ms = 0

        # find the span record and update
        for span in reversed(_ACTIVE_TRACE["spans"]):
            if span.get("span_id") == span_id_to_close:
                if output is not None:
                    span["output"] = output
                if usage:
                    span["usage"].update(usage)
                span["duration_ms"] = duration_ms
                span["success"] = bool(success)
                if error:
                    span["metadata"]["error_message"] = error
                return


def set_span_input(text: str) -> None:
    """Set input text on current active span (no-op if none)."""
    with _LOCK:
        if not _ACTIVE_TRACE.get("stack"):
            return
        cur_span_id = _ACTIVE_TRACE["stack"][-1]["span_id"]
        for span in reversed(_ACTIVE_TRACE["spans"]):
            if span["span_id"] == cur_span_id:
                span["input"] = text
                return


def set_span_usage(usage_dict: Dict[str, Any]) -> None:
    """Set / merge usage dict on current active span (no-op if none)."""
    with _LOCK:
        if not _ACTIVE_TRACE.get("stack"):
            return
        cur_span_id = _ACTIVE_TRACE["stack"][-1]["span_id"]
        for span in reversed(_ACTIVE_TRACE["spans"]):
            if span["span_id"] == cur_span_id:
                span["usage"].update(usage_dict)
                return


def end_trace(
    final_output: Optional[str] = None,
    success: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    End the entire trace. Closes any remaining open spans, computes durations,
    builds the bundle and attempts to send it to Langfuse using send_bundle().
    Returns the bundle dict (useful for tests) or None if nothing to send.
    """
    with _LOCK:
        if not _ACTIVE_TRACE.get("trace_id"):
            return None

        # Close any remaining spans on the stack
        while _ACTIVE_TRACE["stack"]:
            end_span()

        # attach final_output to root span (first span)
        if final_output is not None and _ACTIVE_TRACE["spans"]:
            _ACTIVE_TRACE["spans"][0]["output"] = final_output

        # set success flag on root
        if _ACTIVE_TRACE["spans"]:
            _ACTIVE_TRACE["spans"][0]["success"] = bool(success)

        bundle = {
            "trace_id": _ACTIVE_TRACE["trace_id"],
            "spans": _ACTIVE_TRACE["spans"],
        }

        # Attempt to send to Langfuse (best-effort)
        try:
            if is_enabled():
                send_bundle(bundle)
        except Exception:
            # swallow to keep app resilient
            pass

        # Reset active trace
        _ACTIVE_TRACE["trace_id"] = None
        _ACTIVE_TRACE["spans"] = []
        _ACTIVE_TRACE["stack"] = []

        return bundle
