import json
import boto3
from typing import Optional
from botocore.client import BaseClient  # Correct import for boto3 clients
from .config import get_cfg

# Correct type annotation for the _sqs client
_sqs: Optional[BaseClient] = None  # This is the correct type hint for a boto3 client
_queue_url: Optional[str] = None


def init_sqs_fallback() -> bool:
    """
    Initialize SQS fallback sender.
    Loads AWS profile, region, and queue URL from config.
    """
    global _sqs, _queue_url

    cfg = get_cfg()
    _queue_url = cfg.get("aws_sqs_url")

    if not _queue_url:
        print("[veriskgo] No AWS_SQS_OTEL configured — SQS fallback disabled.")
        return False

    try:
        session = boto3.Session(
            profile_name=cfg.get("aws_profile") or None,
            region_name=cfg.get("aws_region") or "us-east-1",
        )
        _sqs = session.client("sqs")  # This is valid because _sqs is now of type BaseClient
        print(f"[veriskgo] SQS fallback enabled → {_queue_url}")
        return True
    except Exception as e:
        print(f"[veriskgo] Failed to init SQS fallback: {e}")
        _sqs = None
        return False


def send_fallback(trace_bundle: dict) -> bool:
    """
    Sends OTEL bundle to SQS (used when OTLP exporter fails).
    Returns True if message was queued.
    """

    global _sqs, _queue_url

    if _sqs is None or _queue_url is None:
        print("[veriskgo] SQS fallback disabled or not initialized.")
        return False

    try:
        _sqs.send_message(
            QueueUrl=_queue_url,
            MessageBody=json.dumps(trace_bundle)
        )
        print("[veriskgo] Trace sent to SQS fallback queue.")
        return True

    except Exception as e:
        print(f"[veriskgo] ERROR sending to SQS fallback: {e}")
        return False
