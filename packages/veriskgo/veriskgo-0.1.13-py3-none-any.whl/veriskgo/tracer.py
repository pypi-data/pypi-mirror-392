# src/veriskgo/tracer.py

"""
VeriskGO Tracer
----------------

A lightweight, thread-safe tracer for GenAI apps.

The tracer builds a multi-span trace (root + child spans)
and returns a structured bundle ready to send to SQS.

Flow:
  start_trace()  → begin root span
  start_span()   → create nested span
  end_span()     → close span
  end_trace()    → close all + return bundle

No networking is performed here; calling app must send the
bundle to SQS or any custom backend.
"""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

# Global lock for thread safety
_LOCK = threading.Lock()

# Active trace model
_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],
    "stack": [],   # for duration and nesting (LIFO)
}


# -----------------------------
# Internal helpers
# -----------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def current_trace_id() -> Optional[str]:
    with _LOCK:
        return _ACTIVE_TRACE.get("trace_id")
    

# -----------------------------
# Public API
# -----------------------------
def start_trace(
    name: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Starts a new trace and root span. Replaces any existing trace.
    """
    with _LOCK:
        trace_id = _new_id()
        root_span_id = _new_id()

        meta = dict(metadata or {})
        if user_id:
            meta["user_id"] = user_id
        if session_id:
            meta["session_id"] = session_id

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
    Start a nested child span under the current active span.
    """
    with _LOCK:
        if _ACTIVE_TRACE["trace_id"] is None:
            raise RuntimeError("No active trace. Call start_trace() first.")

        parent_id = _ACTIVE_TRACE["stack"][-1]["span_id"] if _ACTIVE_TRACE["stack"] else None
        span_id = _new_id()

        span = {
            "span_id": span_id,
            "parent_span_id": parent_id,
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
    Close a span and compute its duration.
    """
    with _LOCK:
        if _ACTIVE_TRACE["trace_id"] is None:
            return

        # span_id not provided → close last opened span
        if span_id is None:
            if not _ACTIVE_TRACE["stack"]:
                return
            entry = _ACTIVE_TRACE["stack"].pop()
            sid = entry["span_id"]
            duration_ms = int((time.time() - entry["start_time"]) * 1000)
        else:
            sid = span_id
            duration_ms = 0
            for i in range(len(_ACTIVE_TRACE["stack"]) - 1, -1, -1):
                if _ACTIVE_TRACE["stack"][i]["span_id"] == span_id:
                    duration_ms = int((time.time() - _ACTIVE_TRACE["stack"][i]["start_time"]) * 1000)
                    _ACTIVE_TRACE["stack"].pop(i)
                    break

        # update span in the list
        for span in reversed(_ACTIVE_TRACE["spans"]):
            if span["span_id"] == sid:
                if output:
                    span["output"] = output
                if usage:
                    span["usage"].update(usage)
                if error:
                    span["metadata"]["error_message"] = error

                span["duration_ms"] = duration_ms
                span["success"] = success
                return


def end_trace(
    final_output: Optional[str] = None,
    success: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Close all spans, compute durations, and return the full trace bundle.
    Caller is responsible for sending this bundle into SQS.
    """
    with _LOCK:
        if _ACTIVE_TRACE["trace_id"] is None:
            return None

        # close all remaining spans
        while _ACTIVE_TRACE["stack"]:
            end_span()

        # root span modifications
        if _ACTIVE_TRACE["spans"]:
            root = _ACTIVE_TRACE["spans"][0]
            root["success"] = success
            if final_output:
                root["output"] = final_output

        bundle = {
            "trace_id": _ACTIVE_TRACE["trace_id"],
            "spans": _ACTIVE_TRACE["spans"],
        }

        # reset internal state for next trace
        _ACTIVE_TRACE["trace_id"] = None
        _ACTIVE_TRACE["spans"] = []
        _ACTIVE_TRACE["stack"] = []

        return bundle
