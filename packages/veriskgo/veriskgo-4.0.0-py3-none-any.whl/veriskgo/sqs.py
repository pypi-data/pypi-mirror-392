# src/veriskgo/sqs.py
import boto3
import json
from typing import Optional
from .config import get_cfg

_sqs_client  = None
_queue_url: Optional[str] = None

def init_sqs():
    """
    Initializes SQS connection using .env settings.
    """
    global _sqs_client, _queue_url
    
    cfg = get_cfg()
    _queue_url = cfg["sqs_url"]

    session = boto3.Session(
        profile_name=cfg["aws_profile"],
        region_name=cfg["aws_region"]
    )
    _sqs_client = session.client("sqs")

    print(f"[veriskgo] Connected to SQS → {_queue_url}")


def send_to_sqs(trace_bundle: dict) -> bool:
    """
    Sends trace bundle JSON to SQS queue.
    """
    if not _sqs_client or not _queue_url:
        raise RuntimeError("SQS is not initialized. Call init_sqs().")

    try:
        _sqs_client.send_message(
            QueueUrl=_queue_url,
            MessageBody=json.dumps(trace_bundle)
        )
        print("[veriskgo] Trace sent to SQS")
        return True
    except Exception as e:
        print("[veriskgo] ERROR sending to SQS:", e)
        return False
