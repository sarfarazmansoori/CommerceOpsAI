"""Orchestration for AI-powered order investigations."""

from src.agents.investigation_agent import run_investigation_agent
from src.audit.logger import write_audit_event
from src.models import InvestigationResult
from src.policies.rules import evaluate_order
from src.tools.order_tools import get_inventory, get_order


VALID_ACTIONS = {
    "shipment_tracking_stalled": "request_carrier_investigation",
    "inventory_shortage": "escalate_inventory_shortage",
    "order_awaiting_fulfillment": "check_fulfillment_queue",
    "no_known_exception": "review_order_manually",
}


def investigate_order(order_id: str) -> dict:
    """Investigate an order using Bedrock or the deterministic fallback."""

    order = get_order(order_id)
    inventory = get_inventory(order["sku"])

    # The deterministic policy is the evidence-based safety reference.
    policy_decision = evaluate_order(order, inventory)

    # Bedrock uses read-only tools to investigate the same order.
    ai_decision = run_investigation_agent(order_id)

    if ai_decision:
        diagnosis = ai_decision["diagnosis"]
        recommended_action = ai_decision["recommended_action"]

        # Reject a response for a different order.
        if ai_decision.get("order_id") != order_id:
            ai_decision = None

        # Require the AI diagnosis to agree with the evidence-based policy.
        elif diagnosis != policy_decision["diagnosis"]:
            ai_decision = None

        # Reject unsupported diagnosis/action combinations.
        elif VALID_ACTIONS.get(diagnosis) != recommended_action:
            ai_decision = None

    if ai_decision:
        severity = ai_decision["severity"]

        # The policy's approval requirement can never be downgraded.
        requires_approval = (
            policy_decision["requires_human_approval"]
            or severity in ("high", "critical")
        )

        result = {
            "order_id": order_id,
            "diagnosis": diagnosis,
            "evidence": policy_decision["evidence"],
            "recommended_action": recommended_action,
            "requires_human_approval": requires_approval,
            "agent_mode": "bedrock",
            "root_cause": ai_decision["root_cause"],
            "severity": severity,
            "confidence": ai_decision["confidence"],
            "business_impact": ai_decision["business_impact"],
            "resolution_plan": ai_decision["resolution_plan"],
            "tool_calls": ai_decision["tool_calls"],
            "token_usage": ai_decision.get("token_usage", {}),
            "explanation": ai_decision["root_cause"],
        }

    else:
        # Clearly identify deterministic results as fallback, not AI output.
        result = {
            "order_id": order_id,
            **policy_decision,
            "agent_mode": "fallback",
            "root_cause": None,
            "severity": None,
            "confidence": None,
            "business_impact": None,
            "resolution_plan": [],
            "tool_calls": [],
            "token_usage": {},
            "explanation": None,
        }

    validated_result = InvestigationResult.model_validate(result).model_dump()
    write_audit_event(validated_result)

    return validated_result
