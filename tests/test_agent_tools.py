import pytest
from pydantic import ValidationError

from src.agents.tool_registry import execute_tool


def test_agent_can_read_an_order():
    result = execute_tool(
        "get_order",
        {"order_id": "ORD-1002"},
    )

    assert result["order_id"] == "ORD-1002"


def test_agent_can_read_inventory():
    result = execute_tool(
        "get_inventory",
        {"sku": "SKU-HEADPHONES"},
    )

    assert result["available_quantity"] == 0


def test_unregistered_tool_is_rejected():
    with pytest.raises(ValueError, match="not permitted"):
        execute_tool(
            "issue_refund",
            {"order_id": "ORD-1002"},
        )


def test_extra_tool_arguments_are_rejected():
    with pytest.raises(ValidationError):
        execute_tool(
            "get_order",
            {
                "order_id": "ORD-1002",
                "refund_amount": 500,
            },
        )


def test_invalid_order_id_is_rejected():
    with pytest.raises(ValidationError):
        execute_tool(
            "get_order",
            {"order_id": "ORD 1002"},
        )


def test_unknown_order_is_rejected():
    with pytest.raises(ValueError, match="Order not found"):
        execute_tool(
            "get_order",
            {"order_id": "ORD-9999"},
        )
