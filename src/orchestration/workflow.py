"""Orchestrate order investigation and policy evaluation."""

from src.policies.rules import evaluate_order
from src.tools.order_tools import get_inventory, get_order


def investigate_order(order_id: str) -> dict:
    """Investigate an order and return an evidence-based recommendation."""

    order = get_order(order_id)
    inventory = get_inventory(order["sku"])

    result = evaluate_order(order, inventory)

    return {
        "order_id": order_id,
        "diagnosis": result["diagnosis"],
        "evidence": result["evidence"],
        "recommended_action": result["recommended_action"],
        "requires_human_approval": result["requires_human_approval"],
    }
