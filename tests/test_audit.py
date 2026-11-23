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


def test_audit_event_is_uploaded_to_s3(tmp_path, monkeypatch):
    import src.audit.logger as audit_logger

    uploaded_objects = []

    class MockS3Client:
        def put_object(self, **kwargs):
            uploaded_objects.append(kwargs)

    monkeypatch.setenv("S3_AUDIT_BUCKET", "test-audit-bucket")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    monkeypatch.setattr(
        audit_logger.boto3,
        "client",
        lambda service, region_name: MockS3Client(),
    )

    log_path = tmp_path / "audit.jsonl"

    write_audit_event(
        {
            "order_id": "ORD-1002",
            "diagnosis": "inventory_shortage",
        },
        log_path=log_path,
    )

    assert len(uploaded_objects) == 1

    uploaded = uploaded_objects[0]

    assert uploaded["Bucket"] == "test-audit-bucket"
    assert uploaded["Key"].startswith("audit/")
    assert uploaded["ContentType"] == "application/json"

    uploaded_event = json.loads(uploaded["Body"].decode("utf-8"))

    assert uploaded_event["order_id"] == "ORD-1002"
    assert uploaded_event["diagnosis"] == "inventory_shortage"

def test_local_audit_record_remains_if_s3_upload_fails(tmp_path, monkeypatch):
    import src.audit.logger as audit_logger

    class MockS3Client:
        def put_object(self, **kwargs):
            raise RuntimeError("S3 upload failed")

    monkeypatch.setenv("S3_AUDIT_BUCKET", "test-audit-bucket")

    monkeypatch.setattr(
        audit_logger.boto3,
        "client",
        lambda service, region_name: MockS3Client(),
    )

    log_path = tmp_path / "audit.jsonl"

    import pytest

    with pytest.raises(RuntimeError, match="S3 upload failed"):
        write_audit_event(
            {"order_id": "ORD-1003"},
            log_path=log_path,
        )

    records = log_path.read_text(encoding="utf-8").splitlines()

    assert len(records) == 1
    assert json.loads(records[0])["order_id"] == "ORD-1003"
