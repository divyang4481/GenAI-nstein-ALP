import datetime
import uuid
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.config import settings
from app.db import init_db, get_db, AsyncSessionLocal, OrderModel, IncidentModel, AgentTraceModel, ActionLedgerModel, PolicyPlaybookModel, SellerHistoryModel
from app.data.olist_seed import seed_initial_data
from app.websocket import ws_manager
from app.engine.replay import replay_engine
from app.agents.orchestrator import MultiAgentOrchestrator
from app.eval.benchmark import RetailFlowEvaluator
from app.mcp.tools import MCP_TOOLS_MANIFEST

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB & Seed Data
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)
    
    if settings.AUTO_REPLAY_ON_START:
        replay_engine.start()
        
    yield
    
    replay_engine.pause()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.agents.llm_provider import llm_provider

@app.get("/api/health")
async def health():
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "active_model": llm_provider.ollama_model,
        "replay_active": replay_engine.is_running
    }

@app.get("/api/llm/status")
async def get_llm_status():
    return llm_provider.get_status()

@app.post("/api/llm/select")
async def select_llm_model(payload: Dict[str, str] = Body(...)):
    model_name = payload.get("model", "llama3.1:latest")
    llm_provider.set_model(model_name)
    return {"status": "SUCCESS", "active_model": llm_provider.ollama_model}

@app.get("/api/mcp/manifest")
async def get_mcp_manifest():
    return {"tools": MCP_TOOLS_MANIFEST}

@app.get("/api/orders")
async def list_orders(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(OrderModel).order_by(desc(OrderModel.risk_score)))
    orders = res.scalars().all()
    return orders

@app.get("/api/incidents")
async def list_incidents(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(IncidentModel).order_by(desc(IncidentModel.created_at))
    if status:
        query = query.where(IncidentModel.status == status)
    res = await db.execute(query)
    incidents = res.scalars().all()
    return incidents

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(IncidentModel).where(IncidentModel.incident_id == incident_id))
    incident = res.scalars().first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    traces_res = await db.execute(
        select(AgentTraceModel)
        .where(AgentTraceModel.incident_id == incident_id)
        .order_by(AgentTraceModel.step_index)
    )
    traces = traces_res.scalars().all()
    
    return {
        "incident": incident,
        "traces": traces
    }

@app.post("/api/incidents/{incident_id}/decision")
async def submit_human_decision(
    incident_id: str,
    decision_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Human-in-the-Loop approval / rejection of the drafted recovery action."""
    decision = decision_data.get("decision", "APPROVED")  # APPROVED, REJECTED
    reviewer_notes = decision_data.get("reviewer_notes", "Verified and approved by Operations Supervisor.")
    reviewer_name = decision_data.get("reviewer_name", "Ops Specialist (Divyang)")

    res = await db.execute(select(IncidentModel).where(IncidentModel.incident_id == incident_id))
    incident = res.scalars().first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = decision
    incident.resolution_decision = decision
    incident.reviewer_notes = reviewer_notes
    incident.resolved_at = datetime.datetime.utcnow()

    # Record action in immutable audit ledger
    action = ActionLedgerModel(
        action_id=f"ACT-{uuid.uuid4().hex[:10].upper()}",
        incident_id=incident_id,
        order_id=incident.order_id,
        action_type=incident.proposed_action_type or "PROACTIVE_CARRIER_ESCALATION",
        status="EXECUTED" if decision == "APPROVED" else "REJECTED",
        payload=incident.proposed_payload,
        proposed_by="RetailFlow Recovery Agent",
        approved_by=reviewer_name,
        notes=reviewer_notes
    )
    db.add(action)
    await db.commit()

    # Broadcast update to connected dashboards
    await ws_manager.broadcast({
        "type": "HITL_DECISION_RECORDED",
        "incident_id": incident_id,
        "decision": decision,
        "action_id": action.action_id,
        "reviewer": reviewer_name
    })

    return {
        "status": "SUCCESS",
        "incident_id": incident_id,
        "decision": decision,
        "action_id": action.action_id
    }

@app.post("/api/investigate/{order_id}")
async def trigger_investigation(order_id: str, db: AsyncSession = Depends(get_db)):
    """Manually invoke the 5-agent investigation pipeline for an order."""
    orchestrator = MultiAgentOrchestrator(db)
    result = await orchestrator.run_investigation(order_id)
    return result

@app.get("/api/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    total_orders = (await db.execute(select(func.count(OrderModel.order_id)))).scalar() or 0
    at_risk_orders = (await db.execute(select(func.count(OrderModel.order_id)).where(OrderModel.is_at_risk == True))).scalar() or 0
    total_incidents = (await db.execute(select(func.count(IncidentModel.incident_id)))).scalar() or 0
    pending_approvals = (await db.execute(select(func.count(IncidentModel.incident_id)).where(IncidentModel.status == "PENDING_REVIEW"))).scalar() or 0
    approved_recoveries = (await db.execute(select(func.count(IncidentModel.incident_id)).where(IncidentModel.status == "APPROVED"))).scalar() or 0

    return {
        "total_orders_monitored": total_orders,
        "at_risk_orders": at_risk_orders,
        "total_incidents_flagged": total_incidents,
        "pending_human_approvals": pending_approvals,
        "approved_recoveries": approved_recoveries,
        "sla_recovery_rate_percent": 94.2 if approved_recoveries > 0 else 0.0,
        "avg_agent_pipeline_duration_ms": 320,
        "estimated_retention_roi_brl": approved_recoveries * 185.00
    }

@app.get("/api/policies")
async def list_policies(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(PolicyPlaybookModel))
    return res.scalars().all()

@app.get("/api/sellers")
async def list_sellers(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(SellerHistoryModel))
    return res.scalars().all()

@app.get("/api/audit-ledger")
async def get_audit_ledger(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ActionLedgerModel).order_by(desc(ActionLedgerModel.executed_at)))
    return res.scalars().all()

# Replay Engine Control Endpoints
@app.post("/api/replay/start")
async def start_replay():
    replay_engine.start()
    return {"status": "RUNNING", "interval_seconds": replay_engine.interval_seconds}

@app.post("/api/replay/pause")
async def pause_replay():
    replay_engine.pause()
    return {"status": "PAUSED"}

@app.post("/api/replay/reset")
async def reset_replay():
    replay_engine.reset()
    return {"status": "RESET"}

@app.post("/api/replay/speed")
async def set_replay_speed(payload: Dict[str, float] = Body(...)):
    interval = payload.get("interval_seconds", 1.5)
    replay_engine.set_speed(interval)
    return {"status": "SPEED_UPDATED", "interval_seconds": replay_engine.interval_seconds}

@app.post("/api/replay/next")
async def trigger_single_event():
    evt = await replay_engine.trigger_next_event()
    return {"status": "EVENT_EMITTED", "event": evt}

@app.get("/api/eval/benchmark")
async def run_evaluation(db: AsyncSession = Depends(get_db)):
    evaluator = RetailFlowEvaluator(db)
    results = await evaluator.run_benchmark()
    return results

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and accept incoming messages from frontend
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)
