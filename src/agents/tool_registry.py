"""Allow-listed, read-only tools for the CommerceOps AI agent."""

from typing import Callable

from pydantic import BaseModel, ConfigDict, Field

from src.tools.order_tools import get_inventory, get_order


class OrderLookupInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9-]+$",
    )


class InventoryLookupInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sku: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9-]+$",
    )


TOOL_SCHEMAS: dict[str, type[BaseModel]] = {
    "get_order": OrderLookupInput,
    "get_inventory": InventoryLookupInput,
}

TOOL_FUNCTIONS: dict[str, Callable] = {
    "get_order": get_order,
    "get_inventory": get_inventory,
}


def execute_tool(name: str, arguments: dict) -> dict:
    """Execute only a registered tool with validated arguments."""

    if name not in TOOL_SCHEMAS:
        raise ValueError(f"Tool is not permitted: {name}")

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object")

    validated = TOOL_SCHEMAS[name].model_validate(arguments)

    return TOOL_FUNCTIONS[name](**validated.model_dump())
