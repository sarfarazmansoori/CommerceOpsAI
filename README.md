# CommerceOps AI

**An evidence-based e-commerce order investigation API with optional LLM-generated explanations.**

CommerceOps AI is a portfolio project that investigates common e-commerce order exceptions, evaluates deterministic business rules, recommends the next action, and identifies when human approval is required.

The project explores how AI can assist business operations without giving a language model unrestricted control over business decisions.

## Business Problem

E-commerce operations teams routinely investigate:
- Orders delayed during fulfillment
- Inventory shortages
- Shipments with stalled tracking updates

Manual investigation can be repetitive and inconsistent. CommerceOps AI demonstrates a structured workflow for analyzing available evidence and producing consistent recommendations.

## How It Works

1. Receive an order investigation request through a REST API.
2. Retrieve order and inventory data from local sample data.
3. Evaluate the order using deterministic policy rules.
4. Produce a diagnosis, supporting evidence, recommended action, and human-approval requirement.
5. Optionally use Amazon Bedrock to explain the result in plain English.
6. Validate and record the investigation result in a local audit log.

## Architecture

```text
API Request
    |
    v
FastAPI + Request Validation
    |
    v
Investigation Orchestration
    |
    +--> Order and Inventory Tools
    |
    v
Deterministic Policy Engine
    |
    v
Structured Investigation Result
    |
    +--> Optional Amazon Bedrock Explanation
    |       (explanation only)
    |
    v
Response Validation
    |
    v
Local Audit Log + API Response
```

## Key Design Decisions

### Deterministic decision-making

Business rules determine the diagnosis, recommended action, and approval requirement. The language model is not the decision authority.

### Human approval for sensitive actions

The API recommends actions; it does not automatically issue refunds, cancel orders, or modify inventory.

### Optional generative AI

Amazon Bedrock can provide a plain-English explanation of an existing result. It can be disabled through environment configuration.

### Auditability

Investigation results are recorded in a local JSON Lines audit log. The log is intended for development and demonstration, not production-grade audit storage.

### Input and output validation

Pydantic models validate API requests and investigation responses.

## Implemented Technology

- Python
- FastAPI
- Pydantic
- Amazon Bedrock Runtime (`Converse` API), optional
- Boto3
- pytest
- python-dotenv
- Git and GitHub

## Current Implementation Status

**Implemented in the local prototype**
- Order and inventory investigation using sample data
- Deterministic policy evaluation
- Structured investigation results
- Human-approval flags
- Optional Amazon Bedrock explanations
- Local JSON Lines audit logging
- REST API and automated tests

**Not yet implemented**
- AWS Lambda-based deployment
- DynamoDB or S3 persistence
- CloudWatch monitoring
- Docker image and container deployment
- Terraform-managed infrastructure
- GitHub Actions CI/CD pipeline
- Production authentication, authorization, and operational controls

These are potential future extensions, not claims about the current implementation.

## Prerequisites

- Python 3.11 or later
- `pip`
- AWS credentials with appropriate Amazon Bedrock permissions only if testing Bedrock inference

## Local Setup

Clone the repository and enter its directory:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CommerceOpsAI
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Keep Bedrock disabled for local development by setting:

```dotenv
BEDROCK_ENABLED=false
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=
```

Start the API:

```bash
uvicorn src.api.main:app --reload
```

Open the interactive API documentation at:

`http://127.0.0.1:8000/docs`

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Example investigation:

```bash
curl -X POST http://127.0.0.1:8000/investigations \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-1002"}'
```

The sample order IDs are defined in the project's local sample data.

## Optional Amazon Bedrock Integration

To test generative explanations, configure your local `.env` file with:

```dotenv
BEDROCK_ENABLED=true
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0
```

Use AWS credentials configured through a supported AWS credential provider, and ensure the identity has permission to invoke the selected model.

Bedrock inference can incur charges. Keep it disabled unless you intentionally want to test the integration. Never commit `.env` or AWS credentials.

If inference fails, the workflow is designed to retain the deterministic result without an LLM explanation.

## Tests

Run the automated test suite:

```bash
pytest -q
```

The tests cover the API, data tools, policy workflow, validation, audit logging, and the optional Bedrock explanation component.

## Security and Limitations

- Sample orders are for development and demonstration.
- The local audit log is not a centralized or tamper-resistant audit system.
- The current prototype does not implement production authentication or authorization.
- A human-approval flag is a recommendation signal, not a complete approval workflow.
- No production deployment or automated business transaction execution is claimed.

## Roadmap

1. Strengthen policy and failure-path tests.
2. Add containerization and automated CI checks.
3. Define secure, cost-conscious AWS infrastructure using Terraform.
4. Add managed persistence and operational monitoring where justified.
5. Evaluate investigation quality and operational metrics.
6. Implement a controlled human-approval workflow.

## Project Status

Local prototype under active development.
