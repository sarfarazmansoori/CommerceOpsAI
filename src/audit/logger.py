"""Write audit events locally and optionally to Amazon S3."""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import boto3


DEFAULT_LOG_PATH = Path("logs/audit.jsonl")


def write_audit_event(
    event: dict,
    log_path: Path = DEFAULT_LOG_PATH,
) -> None:
    """Write an audit event locally and optionally upload it to S3."""

    timestamp = datetime.now(timezone.utc)

    record = {
        "timestamp": timestamp.isoformat(),
        "event_type": "order_investigation",
        **event,
    }

    serialized_record = json.dumps(record)

    # Always preserve the local audit record.
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as file:
        file.write(serialized_record + "\n")

    # Upload to S3 only when a bucket is configured.
    bucket_name = os.getenv("S3_AUDIT_BUCKET")

    if not bucket_name:
        return

    region = os.getenv("AWS_REGION", "us-east-1")

    date_path = timestamp.strftime("%Y/%m/%d")

    object_key = (
        f"audit/{date_path}/"
        f"{timestamp.strftime('%H%M%S%f')}-{uuid.uuid4().hex}.json"
    )

    s3_client = boto3.client("s3", region_name=region)

    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=serialized_record.encode("utf-8"),
        ContentType="application/json",
    )
