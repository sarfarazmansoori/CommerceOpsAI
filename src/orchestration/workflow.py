"""Orchestrate order investigation and policy evaluation."""

from src.audit.logger import write_audit_event
from src.models import InvestigationResult
from src.policies.rules import evaluate_order
from src.tools.order_tools import get_inventory, get_order


def investigate_order(order_id: str) -> dict:
    """Investigate an order, validate the result, and record it."""

    order = get_order(order_id)
    inventory = get_inventory(order["sku"])

    decision = evaluate_order(order, inventory)

    result = InvestigationResult(
        order_id=order_id,
        **decision,
    )

    validated_result = result.model_dump()

    write_audit_event(validated_result)

    return validated_result
