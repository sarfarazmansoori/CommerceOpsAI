"""REST API for CommerceOps AI."""

from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from src.models import InvestigationResult
from src.orchestration.workflow import investigate_order


load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(
    title="CommerceOps AI",
    description="Evidence-based e-commerce order investigation API",
    version="0.1.0",
)


class InvestigationRequest(BaseModel):
    """Validated request from an API client."""

    model_config = ConfigDict(extra="forbid")

    order_id: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9-]+$",
    )


@app.get("/health")
def health_check() -> dict:
    """Report whether the API process is responsive."""
    return {"status": "healthy"}


@app.post(
    "/investigations",
    response_model=InvestigationResult,
)
def create_investigation(
    request: InvestigationRequest,
) -> InvestigationResult:
    """Investigate an order and return a validated recommendation."""

    try:
        result = investigate_order(request.order_id)
        return InvestigationResult.model_validate(result)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
