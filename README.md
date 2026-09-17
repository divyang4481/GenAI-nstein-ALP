# 🛒 RetailFlow — Real-Time Marketplace Fulfilment Recovery Agent

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Multi--Agent](https://img.shields.io/badge/Multi--Agent-5%20Agents-blueviolet)](https://github.com)
[![MCP](https://img.shields.io/badge/Protocol-MCP%20Tools-FF6B6B)](https://modelcontextprotocol.io)
[![AWS](https://img.shields.io/badge/Cloud%20Target-AWS%20Bedrock%20%2B%20Kinesis-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com)

**RetailFlow** is a demo of an agentic workflow for e-commerce marketplaces. It replays **historical Olist events**, detects fulfilment risks, investigates root causes through an MCP-aligned local tool contract, applies deterministic guardrails, and presents recovery briefs for **Human-in-the-Loop (HITL)** approval.

---

## 🎯 The Problem & The Agentic Solution

* **The Problem:** In a marketplace, thousands of orders move through seller dispatch, regional transit cross-docks, carriers, and last-mile delivery. Operations teams typically discover delays **reactively**—after a 1-star bad review, customer complaint, or order cancellation.
* **The RetailFlow Solution:** A real-time event stream sends order status transitions directly into a 5-agent system. The AI identifies high-risk orders, gathers seller exception histories and transit corridor bottlenecks, checks policy playbooks, drafts proactive courier escalations and customer goodwill credits, and logs approved actions into an immutable ledger.

---

## 🔬 5-Agent Architecture & MCP-aligned Local Tool Contract

```mermaid
flowchart TD
    subgraph Ingestion & Event Stream
        A[Olist Historical Orders Stream] -->|WebSocket 1-3s Replay| B[FastAPI Event Ingestion Pipeline]
        B --> C[(SQLite Database / State Store)]
    end

    subgraph 5-Agent Autonomous Investigation Pipeline
        B --> D[1. Delivery-Risk Agent]
        D -->|High Risk Flag >= 0.65| E[2. Evidence Agent]
        E -->|Local tool calls| F[MCP-aligned Tool Contract]
        E --> G[3. Policy & RAG Agent]
        G -->|RAG Playbooks| F
        G --> H[4. Recovery Agent]
        H --> I[5. Enterprise Guardrail Agent]
    end

    subgraph MCP-aligned Local Tool Layer
        F --> T1[getOrder]
        F --> T2[getSellerHistory]
        F --> T3[findSimilarCases]
        F --> T4[getPolicy]
        F --> T5[escalateCarrier]
        F --> T6[draftCustomerMessage]
    end

    subgraph Human-in-the-Loop & Audit Ledger
        I -->|Audited Action Brief| J[Operations Approval Console]
        J -->|Approve / Reject Action| K[Action Execution Audit Ledger]
    end
```

### The 5 Specialized Agents:
1. **Delivery-Risk Agent:** Calculates delivery risk score (0.0–1.0), SLA burn rate, and delay probability across interstate transit corridors.
2. **Evidence Agent:** Gathers factual evidence via the MCP-aligned local tool contract (`getOrder`, `getSellerHistory`, `findSimilarCases`) highlighting seller late dispatch rates and cross-dock backlogs.
3. **Policy & RAG Agent:** Matches incident context against enterprise fulfillment playbooks (`POL_CARRIER_ESCALATION_01`, `POL_CUSTOMER_PROACTIVE_COMMS_02`), determining permitted actions and voucher caps.
4. **Recovery Agent:** Synthesizes the recovery brief (proactive courier escalation + customer notification draft with compensation credit).
5. **Enterprise Guardrail Agent:** Audits proposed recovery plans against Responsible AI policies:
   * ❌ No autonomous unconditional refunds.
   * ❌ No unsolicited customer messages sent without human review.
   * ✅ Proposed compensation strictly $\le$ policy maximum cap (R$ 25.00).

---

## ☁️ Local MVP to AWS Cloud Production Topology

| Local MVP Component | AWS Production Target | Architecture Role |
| :--- | :--- | :--- |
| **Event Replay Engine** | **Amazon Kinesis Data Streams / MSK** | High-throughput ingestion of marketplace lifecycle events |
| **FastAPI Backend** | **AWS ECS Fargate / Lambda** | Auto-scaling serverless compute container |
| **Multi-Agent AI Engine** | **Amazon Bedrock (Nova Lite default; Nova Pro optional)** | Generative evidence narrative and recommendations; deterministic policy guardrails |
| **WebSocket Manager** | **Amazon API Gateway WebSocket API** | Managed persistent duplex communication with operations consoles |
| **Relational Database** | **Amazon RDS (PostgreSQL Multi-AZ)** | ACID store for orders, SLA configs, and incidents |
| **Audit Ledger** | **Amazon DynamoDB + CloudWatch** | High-durability, immutable audit log for compliance |

---

## 📊 LLM Evaluation & Ground-Truth Benchmarks

RetailFlow includes an isolated evaluation benchmark over labelled historical Olist examples. Metrics are calculated at runtime and are not claims about production performance. Evaluation uses a temporary database and cannot alter live incidents or audit records.

---

## 🚀 Quickstart Guide

### Prerequisites
* Python 3.10+
* Node.js 18+
* AWS credentials available through the normal Boto3 chain (for example an SSO profile or an IAM role)

Copy `backend/.env.example` to `backend/.env`, authenticate the selected `AWS_PROFILE`, and verify that the configured region and IAM policy permit the inference-profile ID. The UI displays **AWS Bedrock • Ready** only after a real smoke invocation succeeds. If it fails, deterministic output remains available but is explicitly labelled **Demo fallback active** and must not be presented as Bedrock inference. The application never shells out to export AWS credentials.

### 1. Start Backend
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`. Swagger API documentation at `http://localhost:8000/docs`.

### 2. Start Frontend
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to interact with the RetailFlow dashboard.

### 3. Run Automated Tests
```powershell
cd backend
pytest tests/test_agents.py -v
```

---

## 🛠️ MCP-aligned Local Tool Contract

The current implementation exposes local Python tool definitions shaped like MCP tools; it does not yet implement an MCP client/server transport.

```json
[
  { "name": "getOrder", "description": "Fetch live Olist order record with pricing, customer geo-location, and SLA deadlines." },
  { "name": "getSellerHistory", "description": "Retrieve seller fulfillment track record, late order rate, and exceptions count." },
  { "name": "findSimilarCases", "description": "Search historical fulfillment resolution cases for similar routes and product categories." },
  { "name": "getPolicy", "description": "Retrieve governing marketplace fulfillment policies and permitted action playbooks." },
  { "name": "createCase", "description": "Initialize a formal operational incident in the recovery ledger." },
  { "name": "escalateCarrier", "description": "Format and dispatch carrier priority escalation tickets." },
  { "name": "draftCustomerMessage", "description": "Generate empathetic customer notification with revised delivery window and credit." }
]
```
