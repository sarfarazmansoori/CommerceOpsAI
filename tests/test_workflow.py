import pytest

from src.orchestration.workflow import investigate_order


def test_inventory_shortage_is_detected():
    result = investigate_order("ORD-1002")

    assert result["diagnosis"] == "inventory_shortage"
    assert result["requires_human_approval"] is True


def test_stalled_tracking_is_detected():
    result = investigate_order("ORD-1003")

    assert result["diagnosis"] == "shipment_tracking_stalled"
    assert result["recommended_action"] == (
        "request_carrier_investigation"
    )


def test_order_awaiting_fulfillment():
    result = investigate_order("ORD-1001")

    assert result["diagnosis"] == "order_awaiting_fulfillment"
    assert result["requires_human_approval"] is False


def test_unknown_order_is_rejected():
    with pytest.raises(ValueError, match="Order not found"):
        investigate_order("ORD-9999")
