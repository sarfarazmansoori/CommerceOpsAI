"""Validated data models for CommerceOps AI."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Diagnosis = Literal[
    "shipment_tracking_stalled",
    "inventory_shortage",
    "order_awaiting_fulfillment",
    "no_known_exception",
]

RecommendedAction = Literal[
    "request_carrier_investigation",
    "escalate_inventory_shortage",
    "check_fulfillment_queue",
    "review_order_manually",
]

Severity = Literal["low", "medium", "high", "critical"]
Confidence = Literal["low", "medium", "high"]
AgentMode = Literal["bedrock", "fallback"]


class InvestigationResult(BaseModel):
    """Validated investigation result returned by the API."""

    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(min_length=1)
    diagnosis: Diagnosis
    evidence: list[str] = Field(min_length=1)
    recommended_action: RecommendedAction
    requires_human_approval: bool

    # AI investigation fields
    agent_mode: AgentMode = "fallback"
    root_cause: str | None = Field(default=None, max_length=500)
    severity: Severity | None = None
    confidence: Confidence | None = None
    business_impact: str | None = Field(default=None, max_length=500)
    resolution_plan: list[str] = Field(default_factory=list)
    tool_calls: list[str] = Field(default_factory=list)
    token_usage: dict[str, int] = Field(default_factory=dict)

    # Human-readable explanation
    explanation: str | None = Field(default=None, max_length=1000)
