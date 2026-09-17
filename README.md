# RetailFlow — Fulfilment Control Tower

RetailFlow is a laptop-runnable enterprise MVP for investigating fulfilment risk in a **historical Olist replay**. It combines a React control tower, FastAPI orchestration, PostgreSQL state, semantic retrieval in Qdrant, Amazon Bedrock generation with a clearly labelled deterministic fallback, a separate MCP Streamable HTTP tool server, deterministic safety rules, and versioned HTTP agent task envelopes.

RetailFlow is a decision-support demonstration. It is not connected to a live marketplace, carrier, CRM, payment system, email provider, or messaging provider.

## Run with Docker

Requirements: Docker Engine with Compose v2 and approximately 4 GB of free memory.

```bash
# Option 1: One-click Python launcher (automatically injects active AWS profile credentials)
python start_docker.py
# (On Windows, you can double-click start_docker.bat)

# Option 2: Direct Docker Compose
docker compose up --build
```

Open <http://localhost:5173>. The API documentation is at <http://localhost:8000/docs>; Qdrant is bound to `127.0.0.1:6333` for local diagnostics only.

Compose starts:

| Service | Role | Health boundary |
|---|---|---|
| `frontend` | React/Vite control tower, port 5173 | HTTP root |
| `backend` | FastAPI orchestration and read-only case Q&A, port 8000 | `/api/health` |
| `postgres` | PostgreSQL 16 operational state | `pg_isready` |
| `qdrant` | `retailflow_knowledge` vector collection | TCP 6333 |
| `mcp-server` | FastMCP tools over MCP Streamable HTTP, internal port 8001 | `/health` |
| `knowledge-ingest` | Idempotent one-shot knowledge indexing | successful exit |

PostgreSQL and Qdrant use named volumes. The backend waits for PostgreSQL, Qdrant, and the MCP service health checks. No credential belongs in source control; use `.env` or your runtime secret store.

## AWS Bedrock credentials

The backend uses the normal Boto3 credential chain. It never shells out for credentials. For a local AWS SSO profile, set `AWS_PROFILE=retailflow-demo`, mount or expose your AWS configuration to the backend container, and grant `bedrock:InvokeModel` for the configured inference profile. On ECS, prefer a task role and leave `AWS_PROFILE` empty.

The deployment-approved generation model is `us.amazon.nova-lite-v1:0`. The header says **AWS Bedrock • Ready** only after a live preflight invocation succeeds. Otherwise it says **Demo fallback active**, and API answers expose `execution_mode=DETERMINISTIC_DEMO_FALLBACK`.

## What is real in this MVP

### Retrieval-augmented generation

`scripts/ingest_knowledge.py` reads versioned policy and historical-case sources from `knowledge/`, creates stable 300–500-word chunks with overlap, generates deterministic local development embeddings, and idempotently upserts them into Qdrant. `RetrievalService` searches four to six chunks and returns source ID, policy/case ID, title, chunk ID, score, version, and excerpt. Policy work is filtered to `source_type=policy`; no retrieved policy means fail-closed.

The local hash embedder keeps an offline laptop demo reliable. It is deliberately identified as a development fallback; a production deployment should inject Amazon Titan Text Embeddings or a managed sentence-transformer service and re-index the collection with the new embedding metadata.

### MCP transport

The backend uses the official MCP Python SDK as a Streamable HTTP client. The separate FastMCP service owns these tools:

* `get_order(order_id)`
* `get_seller_history(seller_id)`
* `find_similar_cases(category, customer_state)`
* `retrieve_policy(query, filters)`
* `create_recovery_draft(order_id, action_payload)`

`MCP_SERVICE_TOKEN` protects `/mcp`. Tool allow-lists are enforced by agent identity in the client. The recovery tool only creates drafts and has no connector capable of executing an external effect. `backend/app/mcp/tools.py` remains only as a legacy test fixture for the original isolated unit tests; the running orchestrator uses `backend/app/mcp/client.py` and never imports the fixture.

### A2A-compatible HTTP envelopes

Each agent publishes a card at `/agents/{agent}/.well-known/agent-card.json`, accepts versioned task envelopes at `POST /agents/{agent}/tasks`, and exposes task state at `GET /agents/{agent}/tasks/{task_id}`. Envelopes preserve task, correlation, parent, sender/receiver, schema version, status, and timestamps. This is a lightweight A2A-compatible boundary, not a claim of full conformance to every feature of an external A2A SDK.

### Safety and action semantics

`GuardrailEngine` is deterministic. It validates the governing policy citation, voucher type/range/cap, BRL currency, supported draft action, human-approval flag, customer-message draft status, and prompt-injection patterns. Contact and payment-shaped data is masked before it can be placed in traces or model context.

The action lifecycle is:

```text
DRAFT → PENDING_REVIEW → APPROVED_FOR_EXECUTION → CONNECTOR_QUEUED → EXECUTED / FAILED
```

This MVP stops at `APPROVED_FOR_EXECUTION`. Approval does **not** claim carrier escalation, customer contact, a refund, or voucher issuance occurred. Case chat is read-only and answers execution requests with a draft-and-review boundary.

## What remains simulated

* Events and orders are a historical Olist replay, never live marketplace data.
* External carrier and CRM connectors do not exist.
* Voucher issuance, refunds, money movement, and customer-message delivery do not exist.
* The retention value is explicitly a demo indicator, not a measured financial outcome.
* The deterministic embedding fallback is intended for laptop development; production should use Titan embeddings.

## Local development without Docker

SQLite remains available only as a practical local/test path. Start Qdrant and the MCP server separately if you want real retrieval and tool transport.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend python scripts/ingest_knowledge.py
cd backend && uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

## Tests and validation

```bash
cd backend && pytest -q
cd frontend && npm run lint && npm run build
docker compose config
```

Tests cover chunking/retrieval citations, deterministic guardrails, the MCP client boundary, A2A correlation envelopes, duplicate incident protection, isolated benchmark state, and the approval lifecycle.

## Presentation demo

1. Run `docker compose up --build` and open the control tower.
2. Confirm the badge honestly reports Bedrock readiness or deterministic fallback.
3. Select an at-risk historical Olist order and run the investigation.
4. Open **AI evidence & trace** to inspect concise rationale, tools, provenance, and safety checks—never private chain-of-thought.
5. Open **Ask this case**, ask which policy permits the voucher, and expand Qdrant source citations.
6. Ask to send a message and observe the read-only authorised-reviewer response.
7. Approve the plan and inspect the **append-only demo audit trail** status `APPROVED_FOR_EXECUTION`.

## Production hardening roadmap

Use migrations rather than startup `create_all`, Secrets Manager for service tokens, TLS/mTLS and workload identity between services, Titan embeddings, an external A2A task worker/queue, row-level tenancy, OpenTelemetry, connector-specific approvals and idempotency keys, retention controls, and an append-only managed audit service before production use.
