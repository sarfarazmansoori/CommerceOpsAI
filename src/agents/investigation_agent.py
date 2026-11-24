"""Bedrock-powered investigation agent with read-only tool access."""

import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.agents.tool_registry import TOOL_SCHEMAS, execute_tool


logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 2

Diagnosis = (
    "shipment_tracking_stalled",
    "inventory_shortage",
    "order_awaiting_fulfillment",
    "no_known_exception",
)

RecommendedAction = (
    "request_carrier_investigation",
    "escalate_inventory_shortage",
    "check_fulfillment_queue",
    "review_order_manually",
)


class AgentDecision(BaseModel):
    """Structured result returned by the AI investigation agent."""

    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(min_length=1, max_length=50)
    diagnosis: str
    root_cause: str = Field(min_length=5, max_length=500)
    severity: str
    confidence: str
    business_impact: str = Field(min_length=5, max_length=500)
    evidence: list[str] = Field(min_length=1, max_length=8)
    recommended_action: str
    resolution_plan: list[str] = Field(min_length=1, max_length=5)


def _read_only_tool_specs() -> list[dict]:
    """Build Bedrock tool definitions from the validated Python registry."""

    descriptions = {
        "get_order": (
            "Retrieve the order record, including status, SKU, quantity, "
            "customer issue, and shipment tracking information."
        ),
        "get_inventory": (
            "Retrieve inventory availability and reorder threshold for a SKU."
        ),
    }

    return [
        {
            "toolSpec": {
                "name": name,
                "description": descriptions[name],
                "inputSchema": {"json": schema.model_json_schema()},
            }
        }
        for name, schema in TOOL_SCHEMAS.items()
    ]


def run_investigation_agent(order_id: str) -> dict | None:
    """
    Run a Bedrock investigation.

    Returns a validated AI decision, or None when Bedrock is unavailable
    or its response cannot be safely validated.
    """

    if os.getenv("BEDROCK_ENABLED", "false").strip().lower() != "true":
        return None

    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
    if not model_id:
        logger.warning("Bedrock is enabled but BEDROCK_MODEL_ID is missing.")
        return None

    region = os.getenv("AWS_REGION", "us-east-1").strip()

    system_prompt = """
You are the investigation agent for an e-commerce operations platform.

You must investigate the requested order using the available tools:
1. Call get_order with the requested order ID.
2. Read the returned SKU and call get_inventory for that SKU.
3. Use the actual returned records to identify the most likely root cause.
4. Do not invent facts, customer information, events, or business records.

Supported diagnoses:
- shipment_tracking_stalled
- inventory_shortage
- order_awaiting_fulfillment
- no_known_exception

Supported recommended actions:
- request_carrier_investigation
- escalate_inventory_shortage
- check_fulfillment_queue
- review_order_manually

Use these diagnosis/action pairings:
- shipment_tracking_stalled -> request_carrier_investigation
- inventory_shortage -> escalate_inventory_shortage
- order_awaiting_fulfillment -> check_fulfillment_queue
- no_known_exception -> review_order_manually

Severity must be low, medium, high, or critical.
Confidence must be low, medium, or high.

Do not issue refunds, cancel orders, change inventory, contact customers,
or perform any operation that modifies business data.
Never claim that an action has been executed. Recommend actions only.
"""

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "text": (
                        f"Investigate order {order_id}. Retrieve its order "
                        "record and corresponding inventory record before "
                        "reaching a conclusion."
                    )
                }
            ],
        }
    ]

    order_record = None
    inventory_record = None
    tools_used: list[str] = []
    token_usage = {
        "inputTokens": 0,
        "outputTokens": 0,
        "totalTokens": 0,
    }

    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        tool_specs = _read_only_tool_specs()

        # The model chooses and invokes the read-only business tools.
        for _ in range(MAX_TOOL_ROUNDS):
            response = client.converse(
                modelId=model_id,
                system=[{"text": system_prompt}],
                messages=messages,
                inferenceConfig={
                    "maxTokens": 350,
                    "temperature": 0.1,
                },
                toolConfig={
                    "tools": tool_specs,
                    "toolChoice": {"auto": {}},
                },
            )

            usage = response.get("usage", {})
            for key in token_usage:
                token_usage[key] += int(usage.get(key, 0))

            assistant_message = response["output"]["message"]
            messages.append(assistant_message)

            if response.get("stopReason") != "tool_use":
                break

            tool_results = []

            for block in assistant_message.get("content", []):
                tool_use = block.get("toolUse")
                if not tool_use:
                    continue

                tool_name = tool_use.get("name", "")
                tool_id = tool_use.get("toolUseId", "")
                arguments = tool_use.get("input", {})

                try:
                    if tool_name not in TOOL_SCHEMAS:
                        raise ValueError("Tool is not allow-listed.")

                    if tool_name == "get_order":
                        if arguments.get("order_id") != order_id:
                            raise ValueError("Requested order ID does not match.")

                    if tool_name == "get_inventory":
                        if not order_record:
                            raise ValueError("Retrieve the order before inventory.")

                        if arguments.get("sku") != order_record.get("sku"):
                            raise ValueError("SKU does not match the retrieved order.")

                    result = execute_tool(tool_name, arguments)

                    if tool_name == "get_order":
                        order_record = result
                    elif tool_name == "get_inventory":
                        inventory_record = result

                    tools_used.append(tool_name)

                    tool_results.append(
                        {
                            "toolResult": {
                                "toolUseId": tool_id,
                                "content": [{"json": result}],
                                "status": "success",
                            }
                        }
                    )

                except (ValueError, ValidationError, TypeError):
                    logger.warning("The agent attempted an invalid tool request.")
                    tool_results.append(
                        {
                            "toolResult": {
                                "toolUseId": tool_id,
                                "content": [
                                    {"text": "Tool request rejected by validation."}
                                ],
                                "status": "error",
                            }
                        }
                    )

            if not tool_results:
                break

            messages.append({"role": "user", "content": tool_results})

        # Both records must have been retrieved successfully.
        if not order_record or not inventory_record:
            logger.warning("Agent did not retrieve all required investigation data.")
            return None

        # Force the model to return its final decision in a validated schema.
        final_tool = {
            "toolSpec": {
                "name": "submit_investigation",
                "description": "Submit the completed structured investigation.",
                "inputSchema": {"json": AgentDecision.model_json_schema()},
            }
        }

        final_response = client.converse(
            modelId=model_id,
            system=[
                {
                    "text": (
                        system_prompt
                        + "\nNow submit your final evidence-based decision "
                        "using the submit_investigation tool. The order and "
                        "inventory records have already been retrieved."
                    )
                }
            ],
            messages=messages,
            inferenceConfig={
                "maxTokens": 450,
                "temperature": 0.1,
            },
            toolConfig={
                "tools": [final_tool],
                "toolChoice": {"tool": {"name": "submit_investigation"}},
            },
        )

        usage = final_response.get("usage", {})
        for key in token_usage:
            token_usage[key] += int(usage.get(key, 0))

        for block in final_response["output"]["message"].get("content", []):
            tool_use = block.get("toolUse")

            if tool_use and tool_use.get("name") == "submit_investigation":
                decision = AgentDecision.model_validate(tool_use["input"])

                if decision.order_id != order_id:
                    raise ValueError("AI response contains a mismatched order ID.")

                if decision.diagnosis not in Diagnosis:
                    raise ValueError("AI returned an unsupported diagnosis.")

                if decision.recommended_action not in RecommendedAction:
                    raise ValueError("AI returned an unsupported recommended action.")

                if decision.severity not in ("low", "medium", "high", "critical"):
                    raise ValueError("AI returned an unsupported severity.")

                if decision.confidence not in ("low", "medium", "high"):
                    raise ValueError("AI returned an unsupported confidence level.")

                return {
                    **decision.model_dump(),
                    "agent_mode": "bedrock",
                    "tool_calls": tools_used,
                    "token_usage": token_usage,
                }

        logger.warning("Bedrock did not return the required investigation result.")
        return None

    except (
        BotoCoreError,
        ClientError,
        KeyError,
        TypeError,
        ValueError,
        ValidationError,
    ):
        logger.exception("Bedrock investigation failed; fallback will be used.")
        return None
