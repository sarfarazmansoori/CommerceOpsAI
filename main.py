"""Command-line entry point for CommerceOps AI."""

import argparse
import json

from src.orchestration.workflow import investigate_order


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Investigate e-commerce order exceptions."
    )
    parser.add_argument(
        "--order-id",
        required=True,
        help="Order ID, for example ORD-1003",
    )
    args = parser.parse_args()

    try:
        result = investigate_order(args.order_id)
    except ValueError as exc:
        parser.exit(status=1, message=f"Error: {exc}\n")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
