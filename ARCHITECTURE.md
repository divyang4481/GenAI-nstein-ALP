# RetailFlow AI - Autonomous Multi-Agent Logistics & Customer Recovery System
## Enterprise Architecture & Technical Specification

---

## 1. Executive Summary & System Overview

**RetailFlow AI** is an autonomous multi-agent incident management and proactive recovery platform built for e-commerce and logistics operations. It continuously analyzes supply-chain event streams, assesses delivery risks, gathers multi-source evidence via **Model Context Protocol (MCP)**, retrieves authoritative corporate policies using **Vector RAG (Qdrant)**, drafts compliant resolution plans with **AWS Bedrock LLMs**, and enforces deterministic **Guardrails** prior to presenting recommendations to human operators via a **Human-in-the-Loop (HITL)** decision console.

```mermaid
graph LR
    A["📦 Order Event Stream"] --> B["⚡ Multi-Agent Orchestrator"]
    B --> C["🔍 5-Stage Agent Pipeline"]
    C --> D["🛡️ Enterprise Guardrails"]
    D --> E["👤 Operations Console (HITL)"]
    E --> F["✅ Automated Case Resolution"]
```

---

## 2. High-Level System Architecture

```mermaid
flowchart TB
    subgraph ClientLayer ["1. Presentation & Interaction Layer"]
        UI["React + Vite UI Dashboard<br/>(Case Workspace, Replay Stream, Case Q&A)"]
        Console["Operations Console<br/>(Human-in-the-Loop Decision Engine)"]
    end

    subgraph APILayer ["2. Orchestration & Backend Service"]
        FastAPI["FastAPI Backend Service<br/>(backend/app/main.py)"]
        Orchestrator["Agent Workflow Orchestrator<br/>(backend/app/agents/orchestrator.py)"]
        LLMProvider["LLM Provider & Router<br/>(backend/app/agents/llm_provider.py)"]
    end

    subgraph AgentsLayer ["3. Specialized Multi-Agent Team"]
        A1["1. Delivery Risk Agent<br/>(Risk Scoring & Delay Assessment)"]
        A2["2. Evidence Retrieval Agent<br/>(Order, Carrier & Seller Inspection)"]
        A3["3. Policy Retrieval Agent<br/>(RAG Knowledge Search)"]
        A4["4. Recovery Action Agent<br/>(Compensation & Communication Drafting)"]
        A5["5. Safety & Guardrail Agent<br/>(Compliance & Financial Limit Checks)"]
    end

    subgraph MCPLayer ["4. Model Context Protocol (MCP) Server"]
        MCPServer["MCP Tool Server (FastMCP / Port 8001)<br/>(mcp-server/app.py)"]
        T1["get_order_details"]
        T2["get_seller_reliability"]
        T3["get_tracking_history"]
        T4["search_policies_rag"]
    end

    subgraph DataIntelligenceLayer ["5. Data & AI Foundation"]
        Bedrock["AWS Bedrock<br/>(Amazon Nova Lite / Claude 3.5 Sonnet)"]
        Qdrant[("Qdrant Vector Database<br/>(Collections: retailflow_knowledge)")]
        Postgres[("PostgreSQL Database<br/>(Olist Orders, Customers, Traces)")]
    end

    %% Wiring
    UI -->|REST API / WebSocket| FastAPI
    Console -->|Approve / Modify / Reject| FastAPI
    FastAPI --> Orchestrator
    Orchestrator --> A1 & A2 & A3 & A4 & A5

    A1 -->|Risk Prompt| LLMProvider
    A2 -->|Tool Calls| MCPServer
    A3 -->|RAG Vector Query| MCPServer
    A4 -->|Draft Generation| LLMProvider
    A5 -->|Safety Verification| LLMProvider

    MCPServer --> T1 & T2 & T3 & T4
    T1 & T2 & T3 --> Postgres
    T4 --> Qdrant

    LLMProvider -->|boto3 API (profile: divyang)| Bedrock

    A5 -.->|Synthesized Case Package| Console
```

---

## 3. The 7-Step Logical Case Flow

```mermaid
flowchart TD
    S1["1. Replay Order Event<br/><i>Ingests delivery anomalies from stream</i>"] --> S2["2. Calculate Risk<br/><i>Estimates churn risk & delay severity</i>"]
    S2 --> S3["3. Retrieve Evidence<br/><i>Fetches tracking, seller & order details via MCP</i>"]
    S3 --> S4["4. Retrieve Policy<br/><i>Searches RAG knowledge base for SLA limits</i>"]
    S4 --> S5["5. Draft Recovery<br/><i>Synthesizes resolution plan & customer message</i>"]
    S5 --> S6["6. Guardrail Check<br/><i>Validates compensation caps & privacy compliance</i>"]
    S6 --> S7["7. Human Decision<br/><i>Specialist reviews, edits, and approves action</i>"]

    style S1 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style S2 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style S3 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style S4 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style S5 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style S6 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style S7 fill:#fef3c7,stroke:#d97706,stroke-width:2px;
```

---

## 4. Multi-Agent Design & Specification

| # | Agent Name | Input Context | Execution Mechanism | Key Output |
|---|---|---|---|---|
| **1** | **Delivery Risk Agent** | Order status, estimated vs actual delivery dates, carrier flags, price | AWS Bedrock / Analytical heuristic | `risk_score` (0.0–1.0), `risk_level` (LOW, MEDIUM, HIGH, CRITICAL), `factors` |
| **2** | **Evidence Agent** | `order_id`, `seller_id`, `customer_id` | MCP Tools (`get_order_details`, `get_seller_reliability`, `get_tracking_history`) | Full order item breakdown, carrier checkpoint timeline, seller reliability score |
| **3** | **Policy Retrieval Agent** | Incident summary, customer tier, delay days | Qdrant Vector Search (`retailflow_knowledge`) | Relevant policy chunks (e.g., `POL-002`, `POL-005`), max voucher limits, SLA rules |
| **4** | **Recovery Action Agent** | Risk score, evidence package, retrieved policies, customer sentiment | AWS Bedrock LLM synthesis | Action type (`CARRIER_ESCALATION`, `VOUCHER_COMPENSATION`, `REFUND`), voucher amount, apology email |
| **5** | **Guardrail Agent** | Drafted recovery plan, policy limits, financial constraints | Deterministic + LLM boundary checks | `status` (`PASSED`, `FLAGGED`, `REJECTED`), compliance violations, corrected output |

---

## 5. End-to-End Execution Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor Specialist as Operations Specialist
    participant UI as React Frontend
    participant FastAPI as FastAPI Backend
    participant Orch as Workflow Orchestrator
    participant MCP as MCP Tool Server (Port 8001)
    participant Postgres as PostgreSQL DB
    participant Qdrant as Qdrant Vector DB
    participant Bedrock as AWS Bedrock (Nova Lite)

    Specialist->>UI: Select Case / Click "Start Agent Investigation"
    UI->>FastAPI: POST /api/cases/{order_id}/investigate
    FastAPI->>Orch: execute_investigation_cycle(order_id)

    %% Step 1 & 2: Risk Calculation
    rect rgb(240, 249, 255)
    Note over Orch,Bedrock: 1. Risk Evaluation Stage
    Orch->>MCP: call_tool("get_order_details", {order_id})
    MCP->>Postgres: SELECT * FROM olist_orders WHERE order_id = :id
    Postgres-->>MCP: Order Record & Delivery Timestamps
    MCP-->>Orch: Order Details
    Orch->>Bedrock: Prompt Delivery Risk Agent (Delay, Value, Carrier History)
    Bedrock-->>Orch: Risk: 0.85 (HIGH), Risk Factors: ["Transit delay > 72h", "High-value item"]
    Orch->>Postgres: INSERT INTO agent_traces (Agent 1: Risk Assessment)
    end

    %% Step 3: Evidence Retrieval
    rect rgb(240, 253, 244)
    Note over Orch,Postgres: 2. Evidence Gathering via MCP
    Orch->>MCP: call_tool("get_seller_reliability", {seller_id})
    MCP->>Postgres: Query seller on-time delivery & review ratings
    Postgres-->>MCP: Rating: 4.8/5, On-Time: 96%
    MCP-->>Orch: Seller Track Record (Tier A)
    Orch->>MCP: call_tool("get_tracking_history", {order_id})
    MCP->>Postgres: Query shipment checkpoints
    Postgres-->>MCP: Checkpoint: Package stuck at distribution hub
    MCP-->>Orch: Tracking Breakdown
    Orch->>Postgres: INSERT INTO agent_traces (Agent 2: Evidence Compiled)
    end

    %% Step 4: Policy Retrieval (RAG)
    rect rgb(254, 252, 232)
    Note over Orch,Qdrant: 3. Policy Retrieval via Vector RAG
    Orch->>MCP: call_tool("search_policies_rag", {query: "Delay > 3 days Tier A seller compensation"})
    MCP->>Qdrant: Vector similarity search (Cosine metric)
    Qdrant-->>MCP: Returns Chunks: POL-002 ($15 max voucher), POL-004 (Carrier SLA escalation)
    MCP-->>Orch: Authoritative Policy Chunks & Rules
    Orch->>Postgres: INSERT INTO agent_traces (Agent 3: Policy Retrieval)
    end

    %% Step 5: Draft Recovery Plan
    rect rgb(254, 242, 242)
    Note over Orch,Bedrock: 4. Draft Recovery Plan
    Orch->>Bedrock: Prompt Recovery Agent (Synthesize Evidence + Policy + Customer Context)
    Bedrock-->>Orch: Recovery Plan: Priority Carrier Dispatch + $10 Courtesy Credit + Apology Draft
    Orch->>Postgres: INSERT INTO agent_traces (Agent 4: Recovery Draft)
    end

    %% Step 6: Guardrail Validation
    rect rgb(250, 245, 255)
    Note over Orch,Bedrock: 5. Safety & Guardrail Check
    Orch->>Bedrock: Prompt Guardrail Agent (Verify $10 <= $15 cap, check tone & PII)
    Bedrock-->>Orch: Status: PASSED (Zero policy violations, verified compliant)
    Orch->>Postgres: INSERT INTO agent_traces (Agent 5: Guardrail Check)
    end

    %% Step 7: Human Decision
    rect rgb(255, 251, 235)
    Note over Orch,Specialist: 6. Human-in-the-Loop Decision Console
    Orch-->>FastAPI: Complete Investigation Payload (5 Traces, Risk, Plan, Email)
    FastAPI-->>UI: Real-time update (WebSocket / REST Response)
    UI-->>Specialist: Render Visual Timeline, Risk Gauge, Policy Cards & Drafted Action
    Specialist->>UI: Review recommendations and click "Approve Action"
    UI->>FastAPI: POST /api/cases/{order_id}/resolve {status: "APPROVED"}
    FastAPI->>Postgres: UPDATE incidents SET status = 'RESOLVED'
    FastAPI-->>UI: Action Confirmed & Incident Closed
    end
```

---

## 6. Agent State Machine & Lifecycle Diagram

```mermaid
stateDiagram-v2
    [*] --> IDLE : System Ready

    IDLE --> RISK_ASSESSMENT : Event Ingested / Triggered
    RISK_ASSESSMENT --> EVIDENCE_GATHERING : Risk Calculated

    state EVIDENCE_GATHERING {
        [*] --> FetchOrderDetails
        FetchOrderDetails --> FetchSellerReliability
        FetchSellerReliability --> FetchTrackingHistory
        FetchTrackingHistory --> [*]
    }

    EVIDENCE_GATHERING --> POLICY_RETRIEVAL : Evidence Package Ready

    state POLICY_RETRIEVAL {
        [*] --> QueryVectorDB
        QueryVectorDB --> MatchPolicyThresholds
        MatchPolicyThresholds --> [*]
    }

    POLICY_RETRIEVAL --> RECOVERY_DRAFTING : Policies Retrieved

    state RECOVERY_DRAFTING {
        [*] --> SynthesizeFacts
        SynthesizeFacts --> FormulateActionPlan
        FormulateActionPlan --> DraftCustomerMessage
        DraftCustomerMessage --> [*]
    }

    RECOVERY_DRAFTING --> GUARDRAIL_VERIFICATION : Draft Completed

    state GUARDRAIL_VERIFICATION {
        [*] --> ValidateFinancialCaps
        ValidateFinancialCaps --> CheckProhibitedContent
        CheckProhibitedContent --> VerifySLAPolicyMatch
        VerifySLAPolicyMatch --> [*]
    }

    GUARDRAIL_VERIFICATION --> HUMAN_APPROVAL : Guardrails Passed
    GUARDRAIL_VERIFICATION --> RECOVERY_DRAFTING : Guardrail Rejected (Auto-Revision)

    state HUMAN_APPROVAL {
        [*] --> PendingReview
        PendingReview --> Approved : Human clicks Approve
        PendingReview --> Modified : Human adjusts compensation / text
        PendingReview --> Rejected : Human rejects action
    }

    Approved --> RESOLVED : Execute Automated Action
    Modified --> RESOLVED : Execute Custom Action
    Rejected --> ESCALATED : Forward to Tier 2 Support

    RESOLVED --> [*]
    ESCALATED --> [*]
```

---

## 7. Interactive Case Q&A (RAG-Powered) Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Specialist as Operations Specialist
    participant UI as Case Q&A UI
    participant FastAPI as Backend (/api/cases/{id}/ask)
    participant Qdrant as Qdrant Vector DB
    participant Bedrock as AWS Bedrock LLM

    Specialist->>UI: Ask: "Why is this order delayed and what is the policy limit?"
    UI->>FastAPI: POST /api/cases/{order_id}/ask {question}
    FastAPI->>FastAPI: Build Case Dossier (Order details, tracking events, incident traces)
    FastAPI->>Qdrant: Vector similarity search for question against policy documents
    Qdrant-->>FastAPI: Relevant Policy Snippets (POL-002, POL-005)
    FastAPI->>Bedrock: System Prompt: Synthesize Answer using Case Dossier + RAG Policies
    Bedrock-->>FastAPI: Grounded Answer with citations & exact reasoning
    FastAPI-->>UI: Return grounded answer + sources
    UI-->>Specialist: Display rich Markdown answer with cited policy references
```

---

## 8. Database Schema & Data Models

```mermaid
erDiagram
    olist_orders ||--o{ olist_order_items : contains
    olist_orders ||--o{ olist_order_payments : paid_by
    olist_orders ||--o{ olist_order_reviews : reviewed_in
    olist_orders ||--o{ incidents : generates
    olist_orders }|--|| olist_customers : placed_by
    olist_order_items }|--|| olist_sellers : fulfilled_by
    olist_order_items }|--|| olist_products : contains_product
    incidents ||--o{ agent_traces : logs

    olist_orders {
        string order_id PK
        string customer_id FK
        string order_status
        timestamp order_purchase_timestamp
        timestamp order_approved_at
        timestamp order_delivered_carrier_date
        timestamp order_delivered_customer_date
        timestamp order_estimated_delivery_date
    }

    incidents {
        string id PK
        string order_id FK
        string incident_type
        string severity
        float risk_score
        string status
        jsonb proposed_action
        string customer_message
        timestamp created_at
        timestamp resolved_at
    }

    agent_traces {
        string id PK
        string incident_id FK
        string agent_name
        string phase
        text thought
        jsonb tool_calls
        jsonb result
        float latency_ms
        int token_count
        timestamp created_at
    }
```

---

## 9. Security, Governance & Deployment Topology

### Deployment Matrix
| Service | Container Name | Port | Base Image | Purpose |
|---|---|---|---|---|
| **Frontend** | `genai-nstein-alp-frontend-1` | `5173` | `node:20-alpine` | React + Vite UI dashboard |
| **Backend** | `genai-nstein-alp-backend-1` | `8000` | `python:3.12-slim` | FastAPI REST/WebSocket server |
| **MCP Server** | `genai-nstein-alp-mcp-server-1` | `8001` | `python:3.12-slim` | FastMCP tool server |
| **Vector DB** | `genai-nstein-alp-qdrant-1` | `6333` | `qdrant/qdrant:v1.15.4` | Vector RAG store |
| **Relational DB** | `genai-nstein-alp-postgres-1` | `5432` | `postgres:16-alpine` | Olist eCommerce dataset & traces |

### Security & Governance Controls
1. **Zero Raw-SQL in Agents**: Agents interact with enterprise data strictly through isolated FastMCP tool interfaces with parameterized queries.
2. **Deterministic Financial Caps**: Guardrails enforce strict policy maximums (e.g., voucher <= $15) at the code level, preventing LLM over-compensation.
3. **Audit Trail**: 100% of agent reasoning chains, tool inputs/outputs, latencies, and human decision logs are recorded in PostgreSQL `agent_traces`.
4. **Credential Isolation**: Temporary AWS session credentials (`AWS_SESSION_TOKEN`) are injected into runtime containers without baking permanent keys into Docker images.

---

## 10. Demo Presentation Guide & Key Talking Points

### Quick Summary of Key Talking Points for Demo
| Stage | Key Technology | Benefit to Highlight |
|---|---|---|
| **Data Extraction** | **FastMCP Server** | Decoupled tool execution; agents never touch raw SQL directly. |
| **Grounding** | **Qdrant Vector DB** | Strict RAG policy retrieval eliminates policy hallucinations. |
| **Reasoning** | **AWS Bedrock (Nova Lite)** | Fast, cost-effective multimodal LLM inference. |
| **Governance** | **Deterministic Guardrails** | Financial limits and compliance are strictly validated. |
| **Auditability** | **Agent Traces Table** | Every thought, tool call, latency, and token count is stored in PostgreSQL for 100% auditable decisions. |

### Step-by-Step Demo Script for Stakeholders

1. **Step 1: Replay Order Event (Trigger)**
   - *Demo Script:* "When an order experiences a delay or anomaly, the event stream triggers the Orchestrator without requiring manual monitoring."
2. **Step 2: Calculate Risk (Delivery Risk Agent)**
   - *Demo Script:* "The Risk Agent immediately assesses the operational and customer churn risk using real-time shipment attributes."
3. **Step 3: Retrieve Evidence (Evidence Agent via MCP Tools)**
   - *Demo Script:* "The Evidence Agent automatically consolidates hard data across disconnected systems—verifying tracking timestamps, vendor track records, and customer lifetime value."
4. **Step 4: Retrieve Policy (Policy Retrieval Agent via Qdrant Vector RAG)**
   - *Demo Script:* "Instead of guessing, the Policy Agent uses RAG over corporate policies to ensure every proposed action strictly adheres to company rules."
5. **Step 5: Draft Recovery (Recovery Action Agent via AWS Bedrock LLM)**
   - *Demo Script:* "The LLM drafts a tailored recovery plan and customer communication personalized to the specific incident and customer history."
6. **Step 6: Guardrail Check (Safety & Compliance Agent)**
   - *Demo Script:* "Our enterprise guardrail checks ensure the AI draft does not exceed budget limits, violate privacy, or make unauthorized commitments."
7. **Step 7: Human Decision (Operations Approval Console)**
   - *Demo Script:* "The human specialist is augmented with all the context and can approve or refine the action in seconds, completing the Human-in-the-Loop governance."

---

## 11. Deep Technical Specifications: Agent Framework, Chunking, Vector DB & Harnessing

### 11.1 Agent Orchestration & Protocol Architecture
- **Framework Type**: Decoupled Deterministic Multi-Agent Framework implemented via FastAPI, Model Context Protocol (MCP), and an explicit Agent-to-Agent (A2A) handoff registry.
- **Why this vs CrewAI / AutoGen**: Avoids non-deterministic looping, unconstrained token burn, and state hallucinations. Every handoff is an explicit immutable JSON envelope containing `task_id`, `correlation_id`, `parent_task_id`, `sender_agent`, and `input_payload`.
- **Tool Execution Isolation**: Agents interact with database tables strictly through FastMCP tool endpoints over `StreamableHTTP` (`http://mcp-server:8001`), completely eliminating direct raw-SQL execution from agent code.

```mermaid
graph TD
    Trigger["Streaming Event Trigger"] --> Orch["MultiAgentOrchestrator"]
    Orch --> A2A["A2A Handoff Protocol (/agents/{id}/tasks)"]
    A2A --> A1["Delivery Risk Agent"]
    A2A --> A2["Evidence Agent"]
    A2A --> A3["Policy Retrieval Agent"]
    A2A --> A4["Recovery Agent"]
    A2A --> A5["Enterprise Guardrail Agent"]
    A1 & A2 & A3 & A4 & A5 --> MCP["FastMCP Tool Server (Port 8001)"]
```

### 11.2 Chunking Strategy & Document Preprocessing
- **Strategy**: **Semantic Sliding-Window Chunking with Metadata Inheritance**.
- **Chunk Window**: `400 words` per chunk (optimized for complete policy clauses and SLA tables).
- **Overlap Buffer**: `50 words` (preserves policy constraints and conditions across chunk boundaries).
- **Metadata Inheritance**: Every chunk inherits source document metadata:
  - `policy_id` (e.g. `POL_CARRIER_ESCALATION_01`, `POL_SELLER_DISPATCH_DELAY_03`)
  - `source_type` (`"policy"` vs `"historical_case"`)
  - `category` (`CARRIER_ESCALATION`, `CUSTOMER_COMMS`, `MERCHANT_SLA`, `GOVERNANCE`)
  - `version` (`"2026.2"`)
  - `max_voucher_brl` (e.g. `25.0`)

### 11.3 Vector Database & Query Architecture
- **Vector DB Engine**: **Qdrant Vector Database v1.15.4** (Rust-native, high-throughput vector store).
- **Collection**: `retailflow_knowledge`
- **Distance Metric**: **Cosine Similarity** ($\cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$).
- **Vector Dimension**: `384` dimensions (dense semantic vector representation).
- **Payload Filtered Search**: Queries utilize payload indexing (`source_type="policy"`) for zero-noise retrieval.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as Policy / Q&A Agent
    participant Retrieval as RetrievalService (retrieval.py)
    participant Qdrant as Qdrant Vector Store (Port 6333)

    Agent->>Retrieval: search(query="Late dispatch seller policy", top_k=5, source_type="policy")
    Retrieval->>Retrieval: Compute Dense Vector (384-dim)
    Retrieval->>Qdrant: Query Points (Cosine + Filter: source_type="policy")
    Qdrant-->>Retrieval: Ranked Results & Payload
    Retrieval->>Retrieval: Apply Relevance Threshold (> 0.45) & Format Citations
    Retrieval-->>Agent: list[RetrievedSource]
```

### 11.4 Reranking & Retrieval Quality Assessment
- **Relevance Threshold**: Scores below `0.45` are discarded.
- **Quality Classification**:
  - `GROUNDED`: Sufficient authoritative policy matches found; citations mapped to exact `policy_id` and `version`.
  - `INSUFFICIENT EVIDENCE`: No qualifying match; system falls back to conservative no-action safety default to prevent hallucinated compensation.

### 11.5 Agent Harnessing & Safety Governance
- **Prompt Injection Defense**: Pre-flight sanitization blocks instruction overrides (e.g. `"ignore previous instructions"`).
- **Deterministic Financial Guardrails**: Hardcoded code assertions verify that proposed goodwill vouchers never exceed policy caps ($\le \text{BRL } 25.00$).
- **Human-in-the-Loop Gateway**: All customer messages and external actions remain in `DRAFT` state until an authorized human specialist approves them.
- **Immutable Audit Ledger**: 100% of agent thoughts, tool inputs, outputs, latencies, and human reviewer decisions are persisted to PostgreSQL `agent_traces` and `action_ledger`.
- **Ground-Truth Evaluation Harness**: Automated benchmarking suite ([`backend/app/eval/benchmark.py`](file:///c:/workspace/CTS_GenAI/Project/GenAI-nstein-ALP/backend/app/eval/benchmark.py)) evaluating Precision, Recall, JSON Validity, and Guardrail Compliance across ground-truth datasets.

### 11.6 Framework Rationale: Why Custom FastAPI + A2A + MCP (Not LangChain / CrewAI / Bedrock Agents)

| Dimension | Custom Harness (FastAPI + A2A + MCP) | CrewAI / AutoGen | LangChain / LangGraph | AWS Bedrock Agents |
|---|---|---|---|---|
| **Safety Governance** | **Deterministic Python Rules** ([`GuardrailEngine`](file:///c:/workspace/CTS_GenAI/Project/GenAI-nstein-ALP/backend/app/guardrails.py)) | Probabilistic LLM self-reflection | Complex graph interceptors | Cloud-managed Guardrails |
| **Tool Execution** | **Model Context Protocol (MCP)** over Streamable HTTP | Custom tool decorators | Python callable wrappers | OpenAPI Action Groups calling Lambda |
| **Inter-Agent Handoffs** | **A2A Task Envelopes** (`task_id`, `correlation_id`, state cards) | Unstructured internal chat loops | Graph channel state | Managed orchestrator routing |
| **Vendor Portability** | **100% Cloud-Agnostic** (AWS Bedrock, Azure OpenAI, GCP, Local) | Portable but dependency-heavy | Portable but high churn | **Strictly locked to AWS** |
| **Auditability** | Complete DB trace persistence (`AgentTraceModel`) | Ephemeral console output | LangSmith SaaS dependency | CloudWatch / AWS X-Ray |

### 11.7 Multi-Tiered Memory Architecture

RetailFlow structures memory across three distinct temporal and functional layers:

1. **Working Memory (In-Flight Investigation Context)**:
   - **Mechanism**: Dynamic memory state passed through A2A HTTP task envelopes.
   - **Scope**: Ephemeral during single-case evaluation; tracks intermediate thoughts, tool outputs, and LLM completions.
2. **Semantic Memory (Knowledge & Precedent Retrieval)**:
   - **Mechanism**: **Qdrant Vector Database** (`retailflow_knowledge` collection) indexing policy playbooks and historical resolution cases with dense Cosine embeddings.
   - **Scope**: Long-term enterprise reference; filtered by source metadata (`source_type`, `category`).
3. **Episodic & Audit Memory (Stateful Operations History)**:
   - **Mechanism**: Relational persistence in **PostgreSQL**:
     - `AgentTraceModel`: Trace ID, parent task, agent identity, tool input/output, execution latency, and token metrics.
     - `ActionLedgerModel`: Immutable audit record of human supervisor approvals, edits, and rejections.
     - `SellerHistoryModel`: Longitudinal performance data across marketplace sellers.

### 11.8 Cloud Platform Mapping: RetailFlow vs AWS Native vs Azure Native

```mermaid
graph TB
    subgraph "RetailFlow Custom Architecture"
        RF_Orch["FastAPI + A2A Envelopes"]
        RF_Tool["FastMCP Server (Port 8001)"]
        RF_Vec["Qdrant Vector Store"]
        RF_Mem["PostgreSQL (Traces & Audit)"]
        RF_LLM["AWS Bedrock (Nova Lite)"]
        RF_Safe["GuardrailEngine (Deterministic)"]
    end

    subgraph "AWS Native Architecture"
        AWS_Orch["Bedrock Multi-Agent / Step Functions"]
        AWS_Tool["Bedrock Action Groups + Lambda"]
        AWS_Vec["Amazon OpenSearch Serverless / Bedrock KB"]
        AWS_Mem["Amazon Aurora PostgreSQL / DynamoDB"]
        AWS_LLM["Amazon Bedrock (Nova / Claude)"]
        AWS_Safe["Amazon Bedrock Guardrails"]
    end

    subgraph "Azure Native Architecture"
        AZ_Orch["Azure AI Agent Service / Semantic Kernel"]
        AZ_Tool["Azure AI Functions / OpenAPI Tools"]
        AZ_Vec["Azure AI Search (Semantic Reranker)"]
        AZ_Mem["Azure Database for PostgreSQL / Cosmos DB"]
        AZ_LLM["Azure OpenAI (GPT-4o)"]
        AZ_Safe["Azure AI Content Safety"]
    end

    RF_Orch -.-> AWS_Orch
    RF_Orch -.-> AZ_Orch
    RF_Tool -.-> AWS_Tool
    RF_Tool -.-> AZ_Tool
    RF_Vec -.-> AWS_Vec
    RF_Vec -.-> AZ_Vec
    RF_Mem -.-> AWS_Mem
    RF_Mem -.-> AZ_Mem
    RF_LLM -.-> AWS_LLM
    RF_LLM -.-> AZ_LLM
    RF_Safe -.-> AWS_Safe
    RF_Safe -.-> AZ_Safe
```


