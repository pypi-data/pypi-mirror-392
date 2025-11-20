# src/veriskgo/tracer.py
from __future__ import annotations
import time
import uuid
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

_LOCK = threading.Lock()

_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],
    "stack": [],
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _id():
    return str(uuid.uuid4())


def start_trace(name: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Start a new trace with a root span."""
    with _LOCK:
        trace_id = _id()
        root_id = _id()

        root_span = {
            "span_id": root_id,
            "parent_span_id": None,
            "name": name,
            "type": "root",
            "timestamp": _now(),
            "input": "",
            "output": "",
            "metadata": metadata or {},
            "usage": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE["trace_id"] = trace_id
        _ACTIVE_TRACE["spans"] = [root_span]
        _ACTIVE_TRACE["stack"] = [{"span_id": root_id, "start": time.time()}]

        return trace_id


def start_span(name: str, input: Optional[str] = None) -> str:
    """Start a child span."""
    with _LOCK:
        parent = _ACTIVE_TRACE["stack"][-1]["span_id"]
        sid = _id()

        span = {
            "span_id": sid,
            "parent_span_id": parent,
            "name": name,
            "type": "child",
            "timestamp": _now(),
            "input": input or "",
            "output": "",
            "metadata": {},
            "usage": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE["spans"].append(span)
        _ACTIVE_TRACE["stack"].append({"span_id": sid, "start": time.time()})

        return sid


def end_span(span_id: Optional[str] = None, output: Optional[str] = None):
    """Finish a span and calculate duration."""
    with _LOCK:
        if not _ACTIVE_TRACE["stack"]:
            return

        # Auto-close last opened span
        if span_id is None:
            entry = _ACTIVE_TRACE["stack"].pop()
            sid = entry["span_id"]
            dur = int((time.time() - entry["start"]) * 1000)
        else:
            sid = span_id
            dur = 0
            for i in reversed(range(len(_ACTIVE_TRACE["stack"]))):
                if _ACTIVE_TRACE["stack"][i]["span_id"] == sid:
                    dur = int((time.time() - _ACTIVE_TRACE["stack"][i]["start"]) * 1000)
                    _ACTIVE_TRACE["stack"].pop(i)
                    break

        # Update the span
        for sp in _ACTIVE_TRACE["spans"]:
            if sp["span_id"] == sid:
                if output:
                    sp["output"] = output
                sp["duration_ms"] = dur
                return


def end_trace(final_output: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Finish all spans and return the full trace bundle."""
    with _LOCK:
        if not _ACTIVE_TRACE["trace_id"]:
            return None

        # Close remaining spans
        while _ACTIVE_TRACE["stack"]:
            end_span()

        # update root
        if final_output:
            _ACTIVE_TRACE["spans"][0]["output"] = final_output

        bundle = {
            "trace_id": _ACTIVE_TRACE["trace_id"],
            "spans": _ACTIVE_TRACE["spans"],
        }

        # reset
        _ACTIVE_TRACE["trace_id"] = None
        _ACTIVE_TRACE["spans"] = []
        _ACTIVE_TRACE["stack"] = []

        return bundle
