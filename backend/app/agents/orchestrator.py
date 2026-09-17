import uuid
import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import OrderModel, IncidentModel, AgentTraceModel
from app.mcp.tools import MCPToolExecutor
from app.agents.risk_agent import DeliveryRiskAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.recovery_agent import RecoveryAgent
from app.agents.guardrail_agent import GuardrailAgent
from app.websocket import ws_manager

class MultiAgentOrchestrator:
    """Coordinates the 5-agent investigation pipeline and persists step-by-step traces."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.mcp = MCPToolExecutor(db)
        self.risk_agent = DeliveryRiskAgent(self.mcp)
        self.evidence_agent = EvidenceAgent(self.mcp)
        self.policy_agent = PolicyAgent(self.mcp)
        self.recovery_agent = RecoveryAgent(self.mcp)
        self.guardrail_agent = GuardrailAgent(self.mcp)

    async def run_investigation(self, order_id: str) -> Dict[str, Any]:
        incident_id = f"INC-{order_id[:8].upper()}-{datetime.datetime.utcnow().strftime('%H%M%S')}"
        traces: List[Dict[str, Any]] = []

        # 1. Delivery-Risk Agent
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Delivery-Risk Agent",
            "step_index": 1,
            "message": f"Calculating fulfillment delay probability and SLA burn rate for {order_id[:8]}..."
        })
        risk_step = await self.risk_agent.evaluate(order_id)
        traces.append(risk_step)
        await self._persist_trace(incident_id, order_id, risk_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": risk_step, "incident_id": incident_id})

        # Check if risk justifies further investigation
        risk_result = risk_step["result"]
        if risk_result["risk_score"] < 0.50:
            return {"incident_id": incident_id, "status": "LOW_RISK_NO_ACTION", "traces": traces}

        # 2. Evidence Agent
        order_data = risk_step["tool_output"]
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Evidence Agent",
            "step_index": 2,
            "message": "Querying seller historical delivery exceptions and similar historical cases..."
        })
        evidence_step = await self.evidence_agent.gather(order_data, risk_result)
        traces.append(evidence_step)
        await self._persist_trace(incident_id, order_id, evidence_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": evidence_step, "incident_id": incident_id})

        # 3. Policy & RAG Agent
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Policy & RAG Agent",
            "step_index": 3,
            "message": "Matching against enterprise SLA playbooks and checking compensation limits..."
        })
        policy_step = await self.policy_agent.check_policies(evidence_step["result"], risk_result)
        traces.append(policy_step)
        await self._persist_trace(incident_id, order_id, policy_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": policy_step, "incident_id": incident_id})

        # 4. Recovery Agent
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Recovery Agent",
            "step_index": 4,
            "message": "Synthesizing recovery brief: carrier escalation draft and customer notification..."
        })
        recovery_step = await self.recovery_agent.draft_recovery(order_data, evidence_step["result"], policy_step["result"])
        traces.append(recovery_step)
        await self._persist_trace(incident_id, order_id, recovery_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": recovery_step, "incident_id": incident_id})

        # 5. Guardrail Agent
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Enterprise Guardrail Agent",
            "step_index": 5,
            "message": "Enforcing Responsible AI boundaries: no unapproved refunds, human sign-off required..."
        })
        guardrail_step = await self.guardrail_agent.validate(recovery_step["result"], policy_step["result"])
        traces.append(guardrail_step)
        await self._persist_trace(incident_id, order_id, guardrail_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": guardrail_step, "incident_id": incident_id})

        # Create Incident record in DB
        incident = IncidentModel(
            incident_id=incident_id,
            order_id=order_id,
            risk_level=risk_result["risk_level"],
            risk_score=risk_result["risk_score"],
            status="PENDING_REVIEW",
            primary_risk_factor=risk_result["primary_risk_factor"],
            evidence_summary=evidence_step["result"]["evidence_summary"],
            recommended_action=recovery_step["result"]["action_brief"],
            guardrail_status=guardrail_step["result"]["guardrail_status"],
            guardrail_notes=guardrail_step["result"]["verdict"],
            proposed_action_type=recovery_step["result"]["action_type"],
            proposed_payload=recovery_step["result"]
        )
        self.db.add(incident)
        
        # Update order risk flag
        res = await self.db.execute(select(OrderModel).where(OrderModel.order_id == order_id))
        order_obj = res.scalars().first()
        if order_obj:
            order_obj.is_at_risk = True
            order_obj.risk_score = risk_result["risk_score"]

        await self.db.commit()

        # Broadcast Incident Creation to dashboard
        await ws_manager.broadcast({
            "type": "INCIDENT_DISPATCHED_FOR_APPROVAL",
            "incident": {
                "incident_id": incident.incident_id,
                "order_id": incident.order_id,
                "risk_level": incident.risk_level,
                "risk_score": incident.risk_score,
                "status": incident.status,
                "primary_risk_factor": incident.primary_risk_factor,
                "recommended_action": incident.recommended_action,
                "guardrail_status": incident.guardrail_status,
                "proposed_payload": incident.proposed_payload,
                "created_at": datetime.datetime.utcnow().isoformat()
            }
        })

        return {
            "incident_id": incident_id,
            "status": "INCIDENT_CREATED",
            "traces": traces,
            "incident": incident
        }

    async def _persist_trace(self, incident_id: str, order_id: str, step_data: Dict[str, Any]):
        trace = AgentTraceModel(
            trace_id=f"TRC-{uuid.uuid4().hex[:12]}",
            incident_id=incident_id,
            order_id=order_id,
            agent_name=step_data["agent_name"],
            step_index=step_data["step_index"],
            thought=step_data.get("thought", ""),
            tool_name=step_data.get("tool_name"),
            tool_input=step_data.get("tool_input"),
            tool_output=step_data.get("tool_output"),
            latency_ms=step_data.get("latency_ms", 0)
        )
        self.db.add(trace)
        await self.db.commit()
