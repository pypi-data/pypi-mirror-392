# src/veriskgo/tracer.py

from __future__ import annotations
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional


_LOCK = threading.Lock()

_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],
    "stack": []
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


def start_trace(name: str = "root", metadata: Dict[str, Any] | None = None):
    """Create root span; required before start_span() works."""
    with _LOCK:
        trace_id = _new_id()
        root_id = _new_id()

        _ACTIVE_TRACE["trace_id"] = trace_id
        _ACTIVE_TRACE["spans"] = [{
            "span_id": root_id,
            "parent_span_id": None,
            "name": name,
            "timestamp": _now(),
            "input": "",
            "output": "",
            "metadata": dict(metadata or {}),
            "duration_ms": 0,
            "success": True,
        }]
        _ACTIVE_TRACE["stack"] = [{"span_id": root_id, "start": time.time()}]

        return trace_id


def start_span(name: str, input: str = ""):
    """Create child span."""
    with _LOCK:
        if _ACTIVE_TRACE["trace_id"] is None:
            raise RuntimeError("start_trace() must be called first")

        parent = _ACTIVE_TRACE["stack"][-1]["span_id"]
        span_id = _new_id()

        span = {
            "span_id": span_id,
            "parent_span_id": parent,
            "name": name,
            "timestamp": _now(),
            "input": input,
            "output": "",
            "metadata": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE["spans"].append(span)
        _ACTIVE_TRACE["stack"].append({"span_id": span_id, "start": time.time()})

        return span_id


def end_span(span_id: str, output: str = "", success: bool = True):
    """Finish span."""
    with _LOCK:
        # pop from stack
        for i in range(len(_ACTIVE_TRACE["stack"]) - 1, -1, -1):
            if _ACTIVE_TRACE["stack"][i]["span_id"] == span_id:
                entry = _ACTIVE_TRACE["stack"].pop(i)
                duration = int((time.time() - entry["start"]) * 1000)
                break
        else:
            duration = 0

        # update span record
        for span in _ACTIVE_TRACE["spans"]:
            if span["span_id"] == span_id:
                span["output"] = output
                span["duration_ms"] = duration
                span["success"] = success
                return


def end_trace(final_output: str = "") -> Dict[str, Any]:
    """Return all spans as bundle but DO NOT send anywhere."""
    with _LOCK:
        # close leftover spans
        while _ACTIVE_TRACE["stack"]:
            sid = _ACTIVE_TRACE["stack"][-1]["span_id"]
            end_span(sid)

        # attach final response
        if _ACTIVE_TRACE["spans"]:
            _ACTIVE_TRACE["spans"][0]["output"] = final_output

        bundle = {
            "trace_id": _ACTIVE_TRACE["trace_id"],
            "spans": _ACTIVE_TRACE["spans"].copy(),
        }

        # reset
        _ACTIVE_TRACE["trace_id"] = None
        _ACTIVE_TRACE["spans"] = []
        _ACTIVE_TRACE["stack"] = []

        return bundle
