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


class InvestigationResult(BaseModel):
    """Validated output of an order investigation."""

    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(min_length=1)
    diagnosis: Diagnosis
    evidence: list[str] = Field(min_length=1)
    recommended_action: RecommendedAction
    requires_human_approval: bool
    explanation: str | None = Field(default=None, max_length=1000)
