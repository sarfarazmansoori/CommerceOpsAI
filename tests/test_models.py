import pytest
from pydantic import ValidationError

from src.models import InvestigationResult


def test_valid_result_is_accepted():
    result = InvestigationResult(
        order_id="ORD-1002",
        diagnosis="inventory_shortage",
        evidence=["Available quantity: 0"],
        recommended_action="escalate_inventory_shortage",
        requires_human_approval=True,
    )

    assert result.diagnosis == "inventory_shortage"


def test_unsupported_action_is_rejected():
    with pytest.raises(ValidationError):
        InvestigationResult(
            order_id="ORD-1002",
            diagnosis="inventory_shortage",
            evidence=["Available quantity: 0"],
            recommended_action="issue_refund",
            requires_human_approval=True,
        )


def test_unexpected_fields_are_rejected():
    with pytest.raises(ValidationError):
        InvestigationResult(
            order_id="ORD-1002",
            diagnosis="inventory_shortage",
            evidence=["Available quantity: 0"],
            recommended_action="escalate_inventory_shortage",
            requires_human_approval=True,
            refund_amount=500,
        )
