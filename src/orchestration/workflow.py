"""Orchestrate order investigation and policy evaluation."""

from src.agents.bedrock_explainer import explain_investigation
from src.audit.logger import write_audit_event
from src.models import InvestigationResult
from src.policies.rules import evaluate_order
from src.tools.order_tools import get_inventory, get_order


def investigate_order(order_id: str) -> dict:
    """Investigate an order, optionally explain it, and record the result."""

    order = get_order(order_id)
    inventory = get_inventory(order["sku"])

    # The deterministic policy engine remains the decision authority.
    decision = evaluate_order(order, inventory)
    result = InvestigationResult(
        order_id=order_id,
        **decision,
    )
    validated_result = result.model_dump()

    # Bedrock can explain the decision but cannot replace it.
    explanation = explain_investigation(validated_result)
    validated_result["explanation"] = explanation

    # Validate the complete response before recording or returning it.
    final_result = InvestigationResult.model_validate(validated_result).model_dump()

    write_audit_event(final_result)

    return final_result
