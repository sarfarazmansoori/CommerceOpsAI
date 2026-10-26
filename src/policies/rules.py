"""Deterministic policies for order exception handling."""


def evaluate_order(order: dict, inventory: dict) -> dict:
    """Diagnose an order issue and recommend a permitted next step."""

    if (
        order["tracking_status"] == "in_transit"
        and order["last_tracking_update_hours"] is not None
        and order["last_tracking_update_hours"] >= 48
    ):
        return {
            "diagnosis": "shipment_tracking_stalled",
            "evidence": [
                f"Tracking status: {order['tracking_status']}",
                (
                    "Hours since last tracking update: "
                    f"{order['last_tracking_update_hours']}"
                ),
            ],
            "recommended_action": "request_carrier_investigation",
            "requires_human_approval": True,
        }

    required_quantity = order["quantity"]
    available_quantity = inventory["available_quantity"]

    if available_quantity < required_quantity:
        return {
            "diagnosis": "inventory_shortage",
            "evidence": [
                f"SKU: {order['sku']}",
                f"Required quantity: {required_quantity}",
                f"Available quantity: {available_quantity}",
            ],
            "recommended_action": "escalate_inventory_shortage",
            "requires_human_approval": True,
        }

    if order["status"] == "processing":
        return {
            "diagnosis": "order_awaiting_fulfillment",
            "evidence": [
                f"Order status: {order['status']}",
                f"Available quantity: {available_quantity}",
            ],
            "recommended_action": "check_fulfillment_queue",
            "requires_human_approval": False,
        }

    return {
        "diagnosis": "no_known_exception",
        "evidence": [f"Order status: {order['status']}"],
        "recommended_action": "review_order_manually",
        "requires_human_approval": True,
    }
