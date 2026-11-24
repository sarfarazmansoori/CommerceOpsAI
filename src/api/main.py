"""REST API and dashboard for CommerceOps AI."""

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field

from src.data.sample_data import ORDERS
from src.models import InvestigationResult
from src.orchestration.workflow import investigate_order


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = PROJECT_ROOT / "src" / "web"
AUDIT_FILE = PROJECT_ROOT / "logs" / "audit.jsonl"

load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

app = FastAPI(
    title="CommerceOps AI",
    description="AI-powered e-commerce order investigation platform",
    version="1.0.0",
)


class InvestigationRequest(BaseModel):
    """Validated investigation request."""

    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9-]+$",
    )


@app.get("/", include_in_schema=False)
def dashboard():
    """Serve the web dashboard."""
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health_check() -> dict:
    """Report API health."""
    return {"status": "healthy"}


@app.get("/orders")
def list_orders() -> list[dict]:
    """Return available synthetic demonstration orders."""
    return [
        {
            "order_id": order["order_id"],
            "status": order["status"],
            "customer_issue": order["customer_issue"],
            "sku": order["sku"],
            "quantity": order["quantity"],
            "tracking_status": order["tracking_status"],
        }
        for order in ORDERS.values()
    ]


@app.get("/investigations")
def list_investigations(limit: int = 20) -> list[dict]:
    """Return the newest locally recorded investigations."""
    if not 1 <= limit <= 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    if not AUDIT_FILE.exists():
        return []

    records = []

    try:
        with AUDIT_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    record = json.loads(line)
                    if record.get("event_type") == "order_investigation":
                        records.append(record)
                except json.JSONDecodeError:
                    continue
    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to read investigation history.",
        )

    return list(reversed(records[-limit:]))


@app.post(
    "/investigations",
    response_model=InvestigationResult,
)
def create_investigation(
    request: InvestigationRequest,
) -> InvestigationResult:
    """Investigate an order and return a validated result."""
    try:
        result = investigate_order(request.order_id)
        return InvestigationResult.model_validate(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
