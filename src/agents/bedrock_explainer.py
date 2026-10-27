"""Optional natural-language explanations using Amazon Bedrock."""

import logging
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)

MAX_EXPLANATION_LENGTH = 1000


def explain_investigation(result: dict) -> str | None:
    """Explain a deterministic result without changing its decision."""

    enabled = os.getenv("BEDROCK_ENABLED", "false").strip().lower()
    if enabled != "true":
        return None

    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
    if not model_id:
        logger.warning("Bedrock is enabled but BEDROCK_MODEL_ID is empty.")
        return None

    region = os.getenv("AWS_REGION", "us-east-1").strip()

    prompt_data = {
        "diagnosis": result["diagnosis"],
        "evidence": result["evidence"],
        "recommended_action": result["recommended_action"],
        "requires_human_approval": result["requires_human_approval"],
    }

    prompt = (
        "Explain this e-commerce order investigation in plain English. "
        "Use only the supplied evidence. Do not change or invent the "
        "diagnosis, recommendation, or approval requirement. Do not "
        "authorize refunds, cancellations, or other business actions. "
        "Keep the explanation under 120 words.\n\n"
        f"Investigation data: {prompt_data}"
    )

    try:
        client = boto3.client("bedrock-runtime", region_name=region)
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            inferenceConfig={
                "maxTokens": 250,
                "temperature": 0.2,
            },
        )

        content = response["output"]["message"]["content"]
        explanation = " ".join(
            block["text"].strip()
            for block in content
            if isinstance(block, dict) and block.get("text")
        ).strip()

        if not explanation:
            return None

        return explanation[:MAX_EXPLANATION_LENGTH]

    except (BotoCoreError, ClientError, KeyError, TypeError, ValueError):
        logger.exception("Bedrock explanation failed; using deterministic result.")
        return None
