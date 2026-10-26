"""Read-only business tools used by the operations workflow."""

from src.data.sample_data import INVENTORY, ORDERS


def get_order(order_id: str) -> dict:
    """Retrieve an order by ID."""
    order = ORDERS.get(order_id)

    if order is None:
        raise ValueError(f"Order not found: {order_id}")

    return order.copy()


def get_inventory(sku: str) -> dict:
    """Retrieve inventory information for a SKU."""
    inventory = INVENTORY.get(sku)

    if inventory is None:
        raise ValueError(f"Inventory record not found: {sku}")

    return inventory.copy()
