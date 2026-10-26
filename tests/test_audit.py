import json

from src.audit.logger import write_audit_event


def test_audit_event_is_written(tmp_path):
    log_path = tmp_path / "audit.jsonl"

    write_audit_event(
        {
            "order_id": "ORD-1002",
            "diagnosis": "inventory_shortage",
        },
        log_path=log_path,
    )

    records = log_path.read_text(encoding="utf-8").splitlines()
    assert len(records) == 1

    event = json.loads(records[0])

    assert event["event_type"] == "order_investigation"
    assert event["order_id"] == "ORD-1002"
    assert event["diagnosis"] == "inventory_shortage"
    assert event["timestamp"]
