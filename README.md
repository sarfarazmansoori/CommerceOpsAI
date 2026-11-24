# CommerceOpsAI

**An AI-powered e-commerce operations investigation agent built with Amazon Bedrock, Python and FastAPI.**

CommerceOpsAI investigates e-commerce order exceptions using an AI agent, read-only business tools and deterministic policy guardrails. It retrieves order and inventory evidence, identifies likely root causes, assesses severity and business impact, and recommends resolution steps.

The system combines agentic AI reasoning with deterministic validation and human oversight.

## 1. Business Problem

E-commerce operations teams regularly investigate:
- Orders delayed during fulfillment
- Inventory shortages
- Shipments with stalled tracking updates

Manual investigation can be repetitive and inconsistent. CommerceOpsAI demonstrates how an AI agent can retrieve relevant operational evidence and produce structured investigations.

## 2. Key Features

- Amazon Bedrock Nova Micro integration.
- Agent-driven read-only tool calling.
- Order and inventory lookup tools.
- Root-cause analysis and severity assessment.
- Business impact and resolution recommendations.
- Deterministic diagnosis and action validation.
- Human-approval enforcement.
- AI and fallback execution modes.
- Local JSON Lines audit logging.
- FastAPI REST API and browser dashboard.
- Docker containerization.
- Terraform infrastructure configuration.
- GitHub Actions CI workflow.

## 3. Architecture

```text
                 Browser Dashboard
                        |
                        v
                  FastAPI API
                        |
                        v
              Investigation Workflow
                        |
             +----------+----------+
             |                     |
             v                     v
       Bedrock AI Agent       Policy Engine
             |                     |
             v                     |
       Tool Registry               |
             |                     |
       +-----+------+              |
       |            |              |
       v            v              |
    Get Order   Get Inventory      |
       |            |              |
       +------+-----+              |
              |                    |
              v                    v
         AI Analysis ------> Validation
                                  |
                                  v
                         Investigation Result
                                  |
                       +----------+----------+
                       |                     |
                       v                     v
                  Dashboard             Audit JSONL
```

The AI agent retrieves operational evidence using allow-listed read-only tools. The deterministic policy engine independently evaluates the same business records.

AI results are accepted only when their diagnosis and recommended action agree with the validated policy outcome. Human-approval requirements cannot be downgraded by the AI.

If Bedrock is disabled or its result is unavailable or rejected, the application uses the deterministic fallback.

See [Architecture Documentation](docs/ARCHITECTURE.md).

## 4. Technology Stack

| Area | Technologies |
|---|---|
| Language | Python 3.12 |
| API | FastAPI, Uvicorn |
| Data validation | Pydantic |
| AI | Amazon Bedrock Runtime, Nova Micro |
| AWS SDK | Boto3 |
| Agent tools | Python read-only tool registry |
| Business logic | Deterministic policy engine |
| Audit logging | JSON Lines |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker |
| Infrastructure as Code | Terraform |
| CI | GitHub Actions |
| Testing | pytest |

## 5. Sample Investigations

The project uses synthetic demonstration data.

| Order | Scenario | Expected diagnosis |
|---|---|---|
| ORD-1001 | Order awaiting fulfillment | order_awaiting_fulfillment |
| ORD-1002 | Inventory unavailable | inventory_shortage |
| ORD-1003 | Tracking update stalled | shipment_tracking_stalled |

Example Bedrock investigation:

- Order: ORD-1002
- Diagnosis: inventory shortage
- Evidence: required quantity 1, available quantity 0
- Severity: high or medium, as assessed by the model
- Recommended action: escalate inventory shortage
- Human approval: required

Model-generated severity and explanatory text may vary between invocations. The diagnosis and action must pass deterministic validation.

## 6. Project Structure

```text
CommerceOpsAI/
├── .github/workflows/ci.yml
├── infrastructure/terraform/
├── src/
│   ├── agents/
│   │   ├── investigation_agent.py
│   │   ├── tool_registry.py
│   │   └── bedrock_explainer.py
│   ├── api/main.py
│   ├── audit/logger.py
│   ├── data/sample_data.py
│   ├── orchestration/workflow.py
│   ├── policies/rules.py
│   ├── tools/order_tools.py
│   ├── web/index.html
│   └── models.py
├── tests/
├── docs/
│   └── ARCHITECTURE.md
├── Dockerfile
├── .dockerignore
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 7. Local Setup

### Prerequisites

- Python 3.12
- Git
- pip
- AWS CLI and AWS credentials for Bedrock inference

### Clone and install

```bash
git clone https://github.com/sarfarazmansoori/CommerceOpsAI.git
cd CommerceOpsAI

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -r requirements.txt
```

### Configure environment

```bash
cp .env.example .env
```

For local fallback mode:

```dotenv
BEDROCK_ENABLED=false
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=
```

### Start the application

```bash
uvicorn src.api.main:app --reload
```

Open the dashboard:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

Health endpoint:

```bash
curl http://localhost:8000/health
```

### Run an investigation

```bash
curl -X POST http://localhost:8000/investigations \
  -H "Content-Type: application/json" \
  -d '{"order_id":"ORD-1002"}'
```

## 8. Amazon Bedrock Configuration

The application supports Amazon Bedrock Converse API with Nova Micro.

Example configuration:

```dotenv
BEDROCK_ENABLED=true
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.amazon.nova-micro-v1:0
```

The AWS identity must have permission to invoke the selected model.

The agent uses a bounded tool-calling workflow with:
- Maximum two tool-selection rounds.
- A 350-token output cap for tool-selection requests.
- A 450-token output cap for the final structured response.
- An allow-list containing only order and inventory lookup tools.

Inference is pay-per-token and can incur AWS charges. Bedrock is disabled by default in `.env.example`.

Never commit AWS credentials or the local `.env` file.

## 9. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/health` | Health check |
| GET | `/orders` | Sample orders |
| GET | `/investigations` | Recent audit history |
| POST | `/investigations` | Investigate an order |

Example POST body:

```json
{
  "order_id": "ORD-1002"
}
```

## 10. Docker

Build:

```bash
docker build -t commerceops-ai:local .
```

Run:

```bash
docker run -d \
  --name commerceops-api \
  -p 8000:8000 \
  -v "$(pwd)/logs:/app/logs" \
  commerceops-ai:local
```

Check:

```bash
docker ps
curl http://localhost:8000/health
```

The Docker image uses a non-root application user and includes a health check. The volume mount preserves local audit records.

Bedrock credentials must be supplied securely at runtime if AI inference is required inside a container. They must never be baked into the image.

## 11. Audit Logging

Investigation events are stored locally in:

```text
logs/audit.jsonl
```

Records include:
- UTC timestamp
- Order ID
- Diagnosis and supporting evidence
- Recommended action
- Human-approval requirement
- Agent execution mode
- AI analysis and resolution plan, when available
- Read-only tool calls
- Token usage

The application records fallback and Bedrock investigations distinctly.

## 12. Terraform Infrastructure

Terraform configuration is provided under `infrastructure/terraform/` for a proposed AWS deployment architecture involving networking, IAM, ECR, ECS/Fargate, S3 and CloudWatch.

Validate configuration:

```bash
cd infrastructure/terraform
terraform init
terraform fmt -check
terraform validate
```

**Deployment status:** Terraform configuration is provided for infrastructure planning and validation. The project has not been deployed to ECS/Fargate.

Running `terraform apply` can create chargeable AWS resources. Review the configuration and cost estimates before deployment.

## 13. CI and Testing

GitHub Actions workflow:

`.github/workflows/ci.yml`

The workflow runs the automated test suite on configured pushes and pull requests.

Run tests locally:

```bash
python -m pytest -q
```

The previous full local test run reported 32 passing tests before the latest token-usage integration changes. Re-run the suite before publishing the final release.

## 14. Security and Limitations

- Only allow-listed read-only business tools are exposed to the AI agent.
- No automatic refunds, cancellations or order modifications are performed.
- Deterministic guardrails validate the AI diagnosis and recommended action.
- Human approval is required where policy or severity demands it.
- AWS credentials are not stored in the repository.
- Synthetic sample data is used.
- Production authentication and authorization are not implemented.
- The human-approval process is represented by a requirement flag, not a complete approval system.
- Local JSONL audit logging is not a production tamper-resistant audit service.
- Production AWS deployment and monitoring have not been verified.

## 15. Project Verification

Verified during development:
- FastAPI application and dashboard.
- Sample order and inventory investigations.
- Dockerized application.
- Deterministic fallback.
- Successful live Bedrock Nova Micro investigation.
- Read-only tool calls to `get_order` and `get_inventory`.
- Structured AI response and token usage.
- Local audit logging.

See the architecture document for the execution flow and design constraints.

---

**Project:** CommerceOpsAI
**Repository:** https://github.com/sarfarazmansoori/CommerceOpsAI
**Purpose:** AI-assisted e-commerce operations investigation portfolio project.
