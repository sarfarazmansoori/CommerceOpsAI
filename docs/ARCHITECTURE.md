# CommerceOpsAI — Architecture

## 1. Overview

CommerceOpsAI is a single-service application. FastAPI serves the REST API and the static browser dashboard. The investigation workflow combines Amazon Bedrock, read-only Python tools, deterministic business policies and local audit logging.

The application is designed to demonstrate bounded agentic reasoning without allowing the model to perform operational write actions.

## 2. Request Lifecycle

1. The dashboard or API submits an order ID.
2. FastAPI validates the request.
3. The workflow retrieves the order and inventory records for deterministic policy evaluation.
4. When enabled, the Bedrock agent receives the investigation task and allow-listed tool definitions.
5. The model requests order and inventory evidence through tool calls.
6. The tool registry validates tool names and arguments before executing the Python functions.
7. The model returns a structured investigation decision.
8. Pydantic validates the response.
9. The orchestration layer checks the requested order ID, diagnosis and diagnosis/action mapping against deterministic policy output.
10. The policy approval requirement is preserved. High or critical AI severity also requires approval.
11. The validated result is returned by FastAPI and written to the local audit log.
12. The dashboard displays the result and execution mode.

## 3. AI Agent and Tool Registry

The Bedrock agent uses the Converse API and a bounded tool-calling loop.

Available tools:

| Tool | Purpose |
|---|---|
| `get_order` | Retrieve a sample order record |
| `get_inventory` | Retrieve inventory for a SKU |

The registry validates arguments using Pydantic schemas and rejects unknown tools.

The agent is not given tools to:
- Issue refunds
- Cancel orders
- Modify inventory
- Change shipment status
- Execute fulfilment operations

The agent can recommend operational steps, but it cannot execute them.

## 4. Deterministic Guardrails

The policy engine independently evaluates the retrieved business records.

The orchestration layer rejects an AI response if:
- The returned order ID does not match the requested order.
- The AI diagnosis differs from the deterministic diagnosis.
- The recommended action does not match the supported diagnosis/action mapping.

Human approval cannot be downgraded by the model. High or critical severity also triggers approval.

When Bedrock is disabled, unavailable or rejected, the workflow returns a deterministic fallback result. The dashboard labels this mode explicitly.

## 5. Result Contract

The structured investigation result contains:
- `order_id`
- `diagnosis`
- `evidence`
- `recommended_action`
- `requires_human_approval`
- `agent_mode`
- `root_cause`
- `severity`
- `confidence`
- `business_impact`
- `resolution_plan`
- `tool_calls`
- `token_usage`
- `explanation`

AI-specific fields are populated only when a Bedrock decision is accepted. Fallback results do not claim AI-generated analysis.

## 6. Observability

The audit logger writes JSON Lines events to `logs/audit.jsonl`.

Events record the investigation timestamp, order ID, diagnosis, evidence, recommendation, approval requirement and execution mode. Accepted Bedrock results additionally include AI analysis, tool calls and token usage.

The API exposes recent records through `GET /investigations`.

## 7. Runtime and Deployment

The local application runs with Uvicorn. Docker packages the FastAPI application and dashboard into one container.

Terraform files describe a proposed AWS infrastructure architecture. They should not be interpreted as proof of a deployed production environment.

## 8. Security Boundaries

- Tool execution is allow-listed.
- Tool inputs are schema-validated.
- The agent has read-only business capabilities.
- No operational write tools are registered.
- Policy validation is independent of model output.
- Human approval requirements are preserved.
- Credentials are provided through runtime AWS configuration, not source code or Docker build layers.

## 9. Current Limitations

- Demonstration data is synthetic and in-memory.
- There is no production order-management integration.
- The approval requirement is recorded as a flag; no approval UI or workflow is implemented.
- Audit records are local JSONL files.
- Production authentication and authorization are not implemented.
- Terraform infrastructure has not been deployed as part of this demonstration.
