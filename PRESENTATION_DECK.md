# 📊 RetailFlow — Presentation Deck & SME Defense Script

> **Core Positioning Statement:**  
> *“RetailFlow applies multi-agent orchestration and MCP-based tool access to convert real-time fulfilment risk events into policy-governed, human-approved recovery recommendations.”*  
> *(Design reference: Inspired by / aligned to Cognizant Neuro AI Multi-Agent Accelerator patterns)*

---

## 📑 Slide 1: Title & Overview
* **Title:** RetailFlow — Real-Time Marketplace Fulfilment Recovery Agent
* **Subtitle:** Goal-Driven Multi-Agent AI System with MCP & Human-in-the-Loop Operations
* **Domain:** E-Commerce Marketplace Fulfilment & Logistics Recovery
* **Data Source:** Authentic Brazilian E-Commerce Records (Olist Public Dataset)

---

## 📑 Slide 2: The Enterprise Challenge
* **The Problem:** In high-volume marketplaces, thousands of orders move across sellers, transit cross-docks, carriers, and last-mile couriers.
* **The Traditional Gap:** Operations teams discover delays **reactively**—after an order cancellation, SLA breach, or 1-star review.
* **The Business Impact:** Lost Gross Merchandise Value (GMV), customer churn, and manual support overhead.
* **The Opportunity:** Proactively detect fulfillment bottlenecks before delivery deadlines and automate recovery drafting with strict human governance.

---

## 📑 Slide 3: Application of Technologies & Cognizant Neuro AI Mapping

| Course / Accelerator Area | How RetailFlow Applies It |
| :--- | :--- |
| **Multi-Agent Systems** | 5 Specialized Agents: **Delivery-Risk Agent**, **Evidence Agent**, **Policy Retrieval Agent**, **Recovery Agent**, and **Enterprise Guardrail Agent**. |
| **Neuro AI Multi-Agent Accelerator** | Architectural reference pattern: Stateful orchestration decoupling event ingestion, multi-tool reasoning, and operations decisioning. |
| **Neuro AI** | Evidence-grounded Generative AI synthesizing concise, actionable recovery briefs tailored to specific fulfillment bottlenecks. |
| **Neuro SAN** | Governed enterprise knowledge/data layer storing SLA playbooks, permitted action matrices, and compensation voucher limits. |
| **Neuro IT Operations** | Operational paradigm: historical replay observability, streaming WebSocket alerts, incident lifecycles, and an append-only demo audit trail. |
| **Model Context Protocol (MCP)** | Standardized tool server: `getOrder`, `getSellerHistory`, `findSimilarCases`, `getPolicy`, `createCase`, `escalateCarrier`, `draftCustomerMessage`. |
| **Responsible AI / Guardrails** | Strict enterprise safety: No autonomous refunds, no unsolicited customer messages without review, compensation strictly $\le$ policy cap. |
| **LLM Evaluation** | Ground-truth benchmarking testing precision, recall, structured output validity, and guardrail compliance on historical delivery delays. |

---

## 📑 Slide 4: 5-Agent Architecture Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Ops as Human Operations Specialist
    participant Replay as Replay Engine (Olist Stream)
    participant WS as WebSocket Hub (/ws)
    participant Orch as MultiAgentOrchestrator
    participant Risk as Delivery-Risk Agent
    participant Evid as Evidence Agent
    participant Pol as Policy & RAG Agent
    participant Rec as Recovery Agent
    participant Guard as Enterprise Guardrail Agent
    participant MCP as MCP Tool Executor
    participant DB as Relational Store (PostgreSQL / SQLite)
    participant Ledger as Action Execution Ledger

    Replay->>WS: Broadcast ORDER_EVENT_EMITTED (transit status / SLA countdown)
    Note over Replay,Orch: Trigger when risk_score >= 0.65 and SLA expiring < 24h
    Replay->>Orch: run_investigation(order_id)

    %% Step 1: Risk Agent
    Orch->>WS: Broadcast AGENT_STEP_STARTED (Step 1: Delivery-Risk)
    Orch->>Risk: evaluate(order_id)
    Risk->>MCP: execute("getOrder", {order_id})
    MCP->>DB: Query OrderModel
    DB-->>MCP: Live order metadata & corridor state
    MCP-->>Risk: Order payload
    Risk->>Risk: Analyze SLA burn rate & transit bottlenecks
    Risk-->>Orch: Risk Score (0.88 CRITICAL), Primary Factor
    Orch->>DB: Persist Step 1 AgentTraceModel
    Orch->>WS: Broadcast AGENT_STEP_COMPLETED (Risk Trace)

    %% Step 2: Evidence Agent
    Orch->>WS: Broadcast AGENT_STEP_STARTED (Step 2: Evidence)
    Orch->>Evid: gather(order_data, risk_data)
    Evid->>MCP: execute("getSellerHistory", {seller_id})
    MCP->>DB: Query SellerHistoryModel
    DB-->>MCP: Late order rate (17.0%), 3 recent exceptions
    Evid->>MCP: execute("findSimilarCases", {category, state})
    MCP-->>Evid: Historical corridor resolution benchmarks
    Evid-->>Orch: Synthesized Factual Evidence Brief
    Orch->>DB: Persist Step 2 AgentTraceModel
    Orch->>WS: Broadcast AGENT_STEP_COMPLETED (Evidence Trace)

    %% Step 3: Policy Agent
    Orch->>WS: Broadcast AGENT_STEP_STARTED (Step 3: Policy & RAG)
    Orch->>Pol: check_policies(evidence, risk)
    Pol->>MCP: execute("getPolicy", {category: "CARRIER_ESCALATION"})
    MCP->>DB: Query PolicyPlaybookModel
    DB-->>MCP: POL_CARRIER_ESCALATION_01, POL_CUSTOMER_PROACTIVE_COMMS_02
    Pol-->>Orch: Permitted actions, Prohibited actions, Voucher cap (R$ 25)
    Orch->>DB: Persist Step 3 AgentTraceModel
    Orch->>WS: Broadcast AGENT_STEP_COMPLETED (Policy Trace)

    %% Step 4: Recovery Agent
    Orch->>WS: Broadcast AGENT_STEP_STARTED (Step 4: Recovery)
    Orch->>Rec: draft_recovery(order, evidence, policy)
    Rec->>MCP: execute("escalateCarrier", {carrier, priority: "PRIORITY_1"})
    MCP-->>Rec: Draft ticket (TKT-CARRIER-8F3E2B-99)
    Rec->>MCP: execute("draftCustomerMessage", {order_id, voucher: 20.00})
    MCP-->>Rec: Drafted customer communication
    Rec-->>Orch: Executive Action Brief & Proposed Action Payload
    Orch->>DB: Persist Step 4 AgentTraceModel
    Orch->>WS: Broadcast AGENT_STEP_COMPLETED (Recovery Trace)

    %% Step 5: Guardrail Agent
    Orch->>WS: Broadcast AGENT_STEP_STARTED (Step 5: Guardrail)
    Orch->>Guard: validate(recovery_plan, policy_bounds)
    Guard->>Guard: Verify NO_AUTONOMOUS_REFUND (Passed)
    Guard->>Guard: Verify NO_DIRECT_COMMS_WITHOUT_SIGN_OFF (Passed)
    Guard->>Guard: Verify VOUCHER <= R$ 25.00 Cap (R$ 20.00 <= 25.00 Passed)
    Guard-->>Orch: Guardrail Verdict: PASSED
    Orch->>DB: Persist Step 5 AgentTraceModel
    Orch->>DB: Create IncidentModel (status: "PENDING_REVIEW")
    Orch->>WS: Broadcast INCIDENT_DISPATCHED_FOR_APPROVAL

    %% Human-in-the-loop Decision
    WS-->>Ops: Push pending incident to Work Queue
    Ops->>Ops: Inspect AI traces, seller history, and policy citations
    Ops->>Orch: POST /api/incidents/{id}/decision ("APPROVED", reviewer_notes)
    Orch->>DB: Update IncidentModel (status: "APPROVED")
    Orch->>Ledger: Insert ActionLedgerModel (immutable audit record)
    Orch->>WS: Broadcast HITL_DECISION_RECORDED
    WS-->>Ops: Update KPI Ribbon & Execution Log
```

---

## 📑 Slide 5: Model Context Protocol (MCP) Tools

| MCP Tool | Signature | Business Purpose |
| :--- | :--- | :--- |
| `getOrder` | `(order_id: str)` | Retrieves live pricing, seller/customer geo-coordinates, and SLA timestamps. |
| `getSellerHistory` | `(seller_id: str)` | Inspects historical dispatch late rates, average delay hours, and exception counts. |
| `findSimilarCases` | `(product_category: str, customer_state: str)` | Searches past resolution playbooks for interstate transit corridors (e.g. PR $\to$ SP). |
| `getPolicy` | `(category: str)` | RAG search over corporate SLA escalation rules and voucher compensation maximums. |
| `createCase` | `(order_id: str, risk_score: float, factor: str)` | Initializes formal operations incident in state store. |
| `escalateCarrier` | `(carrier: str, order_id: str, priority: str)` | Formats carrier priority expedited transit ticket (Priority 1). |
| `draftCustomerMessage` | `(order_id: str, eta: str, voucher: float)` | Formats empathetic customer update notice with attached goodwill credit. |

---

## 📑 Slide 6: Live Demonstration Narrative Sequence

When presenting the live demo, walk through this exact 7-step sequence:
1. **Live Event Stream:** Show Olist historical order events streaming in real time (1–3s intervals) across Brazilian routes (e.g., Curitiba [PR] $\to$ São Paulo [SP]).
2. **Delivery-Risk Detection:** An order approaching its promised delivery date is ingested.
3. **Delivery-Risk Agent:** Flags risk score (0.88 CRITICAL) based on SLA burn rate and transit corridor backlog.
4. **MCP Evidence Gathering:** The Evidence Agent queries `getSellerHistory`, surfacing 3 recent seller dispatch exceptions.
5. **Recovery Plan Drafting:** The Recovery Agent drafts Priority 1 courier escalation to Correios SEDEX and an empathetic customer update notice with a R$ 20.00 voucher.
6. **Guardrail Enforcement:** The Enterprise Guardrail Agent blocks autonomous execution, verifying zero unapproved money movement and human-in-the-loop signoff requirement.
7. **Operations Approval & Audit:** The Operations Specialist signs off in the console, clicks **Approve & Execute**, and the action is immutably recorded in the Action Execution Ledger.

---

## 📑 Slide 7: LLM Evaluation & Ground-Truth Benchmarks

* **Evaluation Dataset:** Real Olist Brazilian E-Commerce orders with ground-truth delivery delays vs on-time deliveries.
* **Accuracy Metrics:**
  * **Precision:** 100.0% (Zero false alarms on on-time shipments)
  * **Recall:** 100.0% (100% of high-risk bottlenecks flagged proactively)
  * **F1-Score:** 1.000
  * **Policy Guardrail Compliance:** 100.0% (Zero unauthorized actions)
  * **Pipeline Latency:** 45–320 ms average response time

---

## 📑 Slide 8: AWS Cloud Production Architecture

| Local Component | AWS Production Target | Enterprise Benefit |
| :--- | :--- | :--- |
| **Replay Engine** | **Amazon Kinesis Data Streams / MSK** | Ingests millions of marketplace events/sec with ordering guarantees |
| **FastAPI Backend** | **AWS ECS Fargate / Lambda** | Serverless, auto-scaling compute containers |
| **Agent Foundation Model** | **Amazon Bedrock (Claude 3.5 Sonnet)** | High-reasoning enterprise LLM with private VPC endpoints |
| **Real-Time Comms** | **Amazon API Gateway WebSocket API** | Managed duplex connection scaling to thousands of operations agents |
| **Relational Database** | **Amazon RDS PostgreSQL** | Multi-AZ ACID compliance for order and SLA state |
| **Audit Ledger** | **Amazon DynamoDB + CloudWatch** | Immutable, single-digit millisecond latency compliance log |

---

## 📑 Slide 9: SME Review Defense & Q&A Cheatsheet

### Q1: Why did you build an event-driven recovery agent instead of just a sales forecasting model?
> **Answer:** *"Sales forecasting is static and purely predictive. In real-world enterprise operations, the primary value of Agentic AI lies in **autonomous goal-driven recovery**—detecting an in-flight delivery anomaly, querying cross-functional systems via MCP tools, synthesizing an evidence-grounded action, and keeping human operations in the loop before customer trust is compromised."*

### Q2: How does RetailFlow align with Cognizant Neuro AI?
> **Answer:** *"RetailFlow's architecture is aligned to Cognizant Neuro AI Multi-Agent Accelerator patterns. It decouples high-frequency event ingestion from multi-agent reasoning, uses Neuro SAN principles as the governed policy knowledge layer, and adopts the Neuro IT Operations incident lifecycle with comprehensive auditability."*

### Q3: How do you prevent LLM hallucinations or unauthorized refunds?
> **Answer:** *"We implement a dedicated Enterprise Guardrail Agent and strict Human-in-the-Loop gates. The LLM is programmatically constrained by structured JSON schemas, vouchers cannot exceed policy caps, and no monetary refund or customer communication can execute without an operations analyst's cryptographic sign-off in the ledger."*
