"""Tests for AI investigation integration and safety guardrails."""

from unittest.mock import patch

from src.orchestration.workflow import investigate_order


def mock_ai_decision(order_id, diagnosis, action, severity="medium"):
    return {
        "order_id": order_id,
        "diagnosis": diagnosis,
        "root_cause": "AI identified the likely operational issue.",
        "severity": severity,
        "confidence": "high",
        "business_impact": "The order may be delayed.",
        "evidence": ["AI evidence"],
        "recommended_action": action,
        "resolution_plan": ["Review the order", "Escalate if necessary"],
        "agent_mode": "bedrock",
        "tool_calls": ["get_order", "get_inventory"],
    }


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_valid_ai_decision_is_used(mock_agent, mock_audit):
    mock_agent.return_value = mock_ai_decision(
        "ORD-1002",
        "inventory_shortage",
        "escalate_inventory_shortage",
    )

    result = investigate_order("ORD-1002")

    assert result["agent_mode"] == "bedrock"
    assert result["diagnosis"] == "inventory_shortage"
    assert result["root_cause"] == "AI identified the likely operational issue."
    assert result["requires_human_approval"] is True
    assert result["tool_calls"] == ["get_order", "get_inventory"]
    mock_audit.assert_called_once()


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_invalid_ai_action_uses_fallback(mock_agent, mock_audit):
    mock_agent.return_value = mock_ai_decision(
        "ORD-1002",
        "inventory_shortage",
        "review_order_manually",
    )

    result = investigate_order("ORD-1002")

    assert result["agent_mode"] == "fallback"
    assert result["diagnosis"] == "inventory_shortage"
    assert result["recommended_action"] == "escalate_inventory_shortage"
    mock_audit.assert_called_once()


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_high_severity_requires_human_approval(mock_agent, mock_audit):
    mock_agent.return_value = mock_ai_decision(
        "ORD-1001",
        "order_awaiting_fulfillment",
        "check_fulfillment_queue",
        severity="critical",
    )

    result = investigate_order("ORD-1001")

    assert result["agent_mode"] == "bedrock"
    assert result["severity"] == "critical"
    assert result["requires_human_approval"] is True


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_bedrock_unavailable_uses_fallback(mock_agent, mock_audit):
    mock_agent.return_value = None

    result = investigate_order("ORD-1003")

    assert result["agent_mode"] == "fallback"
    assert result["diagnosis"] == "shipment_tracking_stalled"
    assert result["recommended_action"] == "request_carrier_investigation"


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_diagnosis_mismatch_uses_fallback(mock_agent, mock_audit):
    mock_agent.return_value = mock_ai_decision(
        "ORD-1002",
        "shipment_tracking_stalled",
        "request_carrier_investigation",
    )

    result = investigate_order("ORD-1002")

    assert result["agent_mode"] == "fallback"
    assert result["diagnosis"] == "inventory_shortage"
    assert result["recommended_action"] == "escalate_inventory_shortage"


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_wrong_order_id_uses_fallback(mock_agent, mock_audit):
    mock_agent.return_value = mock_ai_decision(
        "ORD-1001",
        "inventory_shortage",
        "escalate_inventory_shortage",
    )

    result = investigate_order("ORD-1002")

    assert result["agent_mode"] == "fallback"
    assert result["order_id"] == "ORD-1002"
    assert result["diagnosis"] == "inventory_shortage"


@patch("src.orchestration.workflow.write_audit_event")
@patch("src.orchestration.workflow.run_investigation_agent")
def test_ai_cannot_downgrade_policy_approval(mock_agent, mock_audit):
    mock_agent.return_value = mock_ai_decision(
        "ORD-1002",
        "inventory_shortage",
        "escalate_inventory_shortage",
        severity="low",
    )

    result = investigate_order("ORD-1002")

    assert result["agent_mode"] == "bedrock"
    assert result["severity"] == "low"
    assert result["requires_human_approval"] is True
