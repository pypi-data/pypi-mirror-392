import threading, time, uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

_LOCK = threading.Lock()

_ACTIVE_TRACE: Dict[str, Any] = {
    "trace_id": None,
    "spans": [],
    "stack": [],
}

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def _new_id():
    return str(uuid.uuid4())

def current_trace_id():
    return _ACTIVE_TRACE.get("trace_id")

def start_trace(name: str, user_id: str | None = None, session_id: str | None = None, metadata=None):
    with _LOCK:
        trace_id = _new_id()
        root_id = _new_id()

        meta = dict(metadata or {})
        if user_id: meta["user_id"] = user_id
        if session_id: meta["session_id"] = session_id

        root_span = {
            "span_id": root_id,
            "parent_span_id": None,
            "name": name,
            "operation": "trace.root",
            "timestamp": _now_iso(),
            "input": "",
            "output": "",
            "metadata": meta,
            "usage": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE.update({
            "trace_id": trace_id,
            "spans": [root_span],
            "stack": [{"span_id": root_id, "start_time": time.time()}]
        })

        return trace_id

def start_span(name: str, input: str | None = None, metadata=None):
    with _LOCK:
        parent = _ACTIVE_TRACE["stack"][-1]["span_id"]
        sid = _new_id()

        span = {
            "span_id": sid,
            "parent_span_id": parent,
            "name": name,
            "operation": "span",
            "timestamp": _now_iso(),
            "input": input or "",
            "output": "",
            "metadata": dict(metadata or {}),
            "usage": {},
            "duration_ms": 0,
            "success": True,
        }

        _ACTIVE_TRACE["spans"].append(span)
        _ACTIVE_TRACE["stack"].append({"span_id": sid, "start_time": time.time()})
        return sid

def end_span(span_id=None, output=None, usage=None, success=True, error=None):
    with _LOCK:
        if span_id is None:
            entry = _ACTIVE_TRACE["stack"].pop()
            sid = entry["span_id"]
            duration = int((time.time() - entry["start_time"]) * 1000)
        else:
            sid = span_id
            duration = 0
            for i in range(len(_ACTIVE_TRACE["stack"]) - 1, -1, -1):
                if _ACTIVE_TRACE["stack"][i]["span_id"] == sid:
                    duration = int((time.time() - _ACTIVE_TRACE["stack"][i]["start_time"]) * 1000)
                    _ACTIVE_TRACE["stack"].pop(i)
                    break

        for span in reversed(_ACTIVE_TRACE["spans"]):
            if span["span_id"] == sid:
                if output: span["output"] = output
                if usage: span["usage"].update(usage)
                if error: span["metadata"]["error_message"] = error
                span["duration_ms"] = duration
                span["success"] = success
                return

def end_trace(final_output=None, success=True):
    with _LOCK:
        while _ACTIVE_TRACE["stack"]:
            end_span()

        if _ACTIVE_TRACE["spans"]:
            root = _ACTIVE_TRACE["spans"][0]
            root["success"] = success
            if final_output: root["output"] = final_output

        bundle = {
            "trace_id": _ACTIVE_TRACE["trace_id"],
            "spans": _ACTIVE_TRACE["spans"],
        }

        _ACTIVE_TRACE.update({"trace_id": None, "spans": [], "stack": []})
        return bundle
