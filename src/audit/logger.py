"""Append investigation events to a local JSON Lines audit file."""

import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_LOG_PATH = Path("logs/audit.jsonl")


def write_audit_event(
    event: dict,
    log_path: Path = DEFAULT_LOG_PATH,
) -> None:
    """Write one timestamped event as a JSON Lines record."""

    log_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "order_investigation",
        **event,
    }

    with log_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
