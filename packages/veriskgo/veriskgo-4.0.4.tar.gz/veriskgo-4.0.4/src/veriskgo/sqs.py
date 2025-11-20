# src/veriskgo/sqs.py
import json
import boto3
from typing import Optional, Dict, Any
from .config import get_cfg

_sqs = None
_queue_url: Optional[str] = None


def init_sqs() -> bool:
    """Initialize SQS client from .env config."""
    global _sqs, _queue_url

    cfg = get_cfg()
    _queue_url = cfg.get("aws_sqs_url")

    if not _queue_url:
        print("[veriskgo] No SQS URL found in .env → fallback disabled.")
        return False

    session = boto3.Session(
        profile_name=cfg.get("aws_profile"),
        region_name=cfg.get("aws_region", "us-east-1")
    )

    _sqs = session.client("sqs")
    print(f"[veriskgo] SQS initialized → {_queue_url}")
    return True


def send_to_sqs(trace_bundle: Optional[Dict[str, Any]]) -> bool:
    """Safely send a trace bundle to SQS."""
    if trace_bundle is None:
        print("[veriskgo] No trace bundle, skipping SQS send.")
        return False

    if not _sqs or not _queue_url:
        print("[veriskgo] SQS not initialized, cannot send.")
        return False

    try:
        _sqs.send_message(
            QueueUrl=_queue_url,
            MessageBody=json.dumps(trace_bundle)
        )
        print("[veriskgo] Trace bundle sent to SQS.")
        return True

    except Exception as e:
        print(f"[veriskgo] ERROR sending to SQS → {e}")
        return False
