# src/veriskgo/tracer.py
import time
import uuid
from datetime import datetime, timezone
import threading
from typing import Dict, Any, Optional

_LOCK = threading.Lock()

_ACTIVE = {
    "trace_id": None,
    "spans": [],
    "stack": []
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def _id():
    return str(uuid.uuid4())


# -------- TRACE --------
def start_trace(name: str, metadata: Dict[str, Any] | None = None) -> str:
    with _LOCK:
        trace_id = _id()
        root_id = _id()

        span = {
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
            "success": True
        }

        _ACTIVE["trace_id"] = trace_id
        _ACTIVE["spans"] = [span]
        _ACTIVE["stack"] = [{"id": root_id, "start": time.time()}]
        return trace_id


# -------- SPAN --------
def start_span(name: str, input: Optional[str] = None) -> str:
    with _LOCK:
        if not _ACTIVE["trace_id"]:
            raise RuntimeError("Call start_trace() first.")

        parent = _ACTIVE["stack"][-1]["id"]
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
            "success": True
        }

        _ACTIVE["spans"].append(span)
        _ACTIVE["stack"].append({"id": sid, "start": time.time()})
        return sid


# -------- END SPAN --------
def end_span(span_id: Optional[str] = None, output=None, usage=None, success=True):
    with _LOCK:
        if not _ACTIVE["trace_id"]:
            return

        # auto-pop if not provided
        if span_id is None:
            entry = _ACTIVE["stack"].pop()
            sid = entry["id"]
            duration = int((time.time() - entry["start"]) * 1000)
        else:
            sid = span_id
            duration = 0
            for i in range(len(_ACTIVE["stack"])-1, -1, -1):
                if _ACTIVE["stack"][i]["id"] == span_id:
                    duration = int((time.time() - _ACTIVE["stack"][i]["start"]) * 1000)
                    _ACTIVE["stack"].pop(i)
                    break

        # update span
        for s in reversed(_ACTIVE["spans"]):
            if s["span_id"] == sid:
                if output: s["output"] = output
                if usage: s["usage"] = usage
                s["success"] = success
                s["duration_ms"] = duration
                return


# -------- END TRACE --------
def end_trace(final_output=None, success=True):
    with _LOCK:
        if not _ACTIVE["trace_id"]:
            return None

        # close remaining spans
        while _ACTIVE["stack"]:
            end_span()

        # update root
        root = _ACTIVE["spans"][0]
        root["success"] = success
        if final_output:
            root["output"] = final_output

        bundle = {
            "trace_id": _ACTIVE["trace_id"],
            "spans": _ACTIVE["spans"]
        }

        # reset
        _ACTIVE["trace_id"] = None
        _ACTIVE["spans"] = []
        _ACTIVE["stack"] = []

        return bundle
