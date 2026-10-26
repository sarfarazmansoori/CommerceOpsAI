from fastapi.testclient import TestClient

from src.api.main import app
from src.orchestration import workflow


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_investigation_endpoint(monkeypatch):
    monkeypatch.setattr(
        workflow,
        "write_audit_event",
        lambda event: None,
    )

    response = client.post(
        "/investigations",
        json={"order_id": "ORD-1002"},
    )

    assert response.status_code == 200
    assert response.json()["diagnosis"] == "inventory_shortage"
    assert response.json()["requires_human_approval"] is True


def test_unknown_order_returns_404():
    response = client.post(
        "/investigations",
        json={"order_id": "ORD-9999"},
    )

    assert response.status_code == 404


def test_extra_request_fields_are_rejected():
    response = client.post(
        "/investigations",
        json={
            "order_id": "ORD-1002",
            "refund_amount": 500,
        },
    )

    assert response.status_code == 422


def test_invalid_order_id_format_is_rejected():
    response = client.post(
        "/investigations",
        json={"order_id": "ORD 1002"},
    )

    assert response.status_code == 422
