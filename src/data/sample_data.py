"""Synthetic order and inventory data for local development."""

ORDERS = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "status": "processing",
        "sku": "SKU-MOUSE",
        "quantity": 2,
        "customer_issue": "Where is my order?",
        "tracking_status": "not_shipped",
        "last_tracking_update_hours": None,
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "status": "processing",
        "sku": "SKU-HEADPHONES",
        "quantity": 1,
        "customer_issue": "My order has not shipped.",
        "tracking_status": "not_shipped",
        "last_tracking_update_hours": None,
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "status": "shipped",
        "sku": "SKU-MOUSE",
        "quantity": 1,
        "customer_issue": "My tracking has not updated.",
        "tracking_status": "in_transit",
        "last_tracking_update_hours": 72,
    },
}

INVENTORY = {
    "SKU-MOUSE": {
        "sku": "SKU-MOUSE",
        "available_quantity": 20,
        "reorder_threshold": 10,
    },
    "SKU-HEADPHONES": {
        "sku": "SKU-HEADPHONES",
        "available_quantity": 0,
        "reorder_threshold": 5,
    },
}
