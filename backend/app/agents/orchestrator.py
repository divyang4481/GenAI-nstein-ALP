import uuid
import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db import OrderModel, IncidentModel, AgentTraceModel
from app.mcp.client import MCPClient
from app.agents.risk_agent import DeliveryRiskAgent
from app.agents.evidence_agent import EvidenceAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.recovery_agent import RecoveryAgent
from app.agents.guardrail_agent import GuardrailAgent
from app.websocket import ws_manager
from app.agents.llm_provider import llm_provider
from app.a2a import A2AGateway
from app.security import mask_pii

class MultiAgentOrchestrator:
    """Coordinates the 5-agent investigation pipeline and persists step-by-step traces."""

    def __init__(self, db: AsyncSession, mcp_client=None, a2a_gateway=None):
        self.db = db
        self.mcp = mcp_client or MCPClient()
        self.a2a = a2a_gateway if a2a_gateway is not None else (A2AGateway() if mcp_client is None else None)
        self.risk_agent = DeliveryRiskAgent(self.mcp)
        self.evidence_agent = EvidenceAgent(self.mcp)
        self.policy_agent = PolicyAgent(self.mcp)
        self.recovery_agent = RecoveryAgent(self.mcp)
        self.guardrail_agent = GuardrailAgent(self.mcp)

    async def run_investigation(self, order_id: str) -> Dict[str, Any]:
        # Clean up any previous incident or traces for this order so investigation runs fresh
        existing_incidents = (await self.db.execute(
            select(IncidentModel).where(IncidentModel.order_id == order_id)
        )).scalars().all()
        for old_inc in existing_incidents:
            await self.db.execute(
                delete(AgentTraceModel).where(
                    (AgentTraceModel.incident_id == old_inc.incident_id) | (AgentTraceModel.order_id == order_id)
                )
            )
            await self.db.delete(old_inc)
        await self.db.flush()

        incident_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())
        parent_task_id = None
        traces: List[Dict[str, Any]] = []

        order = (await self.db.execute(select(OrderModel).where(OrderModel.order_id == order_id))).scalars().first()
        if not order:
            raise LookupError(f"Order {order_id} not found")

        # 1. Delivery-Risk Agent
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Delivery-Risk Agent",
            "step_index": 1,
            "message": f"Calculating fulfillment delay probability and SLA burn rate for {order_id[:8]}..."
        })
        risk_task = await self._submit_handoff("risk", "Assess delivery risk", {"order_id": order_id}, correlation_id, parent_task_id, "orchestrator")
        parent_task_id = risk_task.get("task_id")
        risk_step = await self.risk_agent.evaluate(order_id)
        await self._complete_handoff("risk", risk_task, risk_step["result"])
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
        evidence_task = await self._submit_handoff("evidence", "Gather factual incident evidence", {"order_id": order_id, "risk": risk_result}, correlation_id, parent_task_id, "Delivery-Risk Agent")
        parent_task_id = evidence_task.get("task_id")
        evidence_step = await self.evidence_agent.gather(order_data, risk_result)
        await self._complete_handoff("evidence", evidence_task, evidence_step["result"])
        traces.append(evidence_step)
        await self._persist_trace(incident_id, order_id, evidence_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": evidence_step, "incident_id": incident_id})

        # 3. Policy Retrieval Agent
        await ws_manager.broadcast({
            "type": "AGENT_STEP_STARTED",
            "order_id": order_id,
            "incident_id": incident_id,
            "agent_name": "Policy Retrieval Agent",
            "step_index": 3,
            "message": "Matching against enterprise SLA playbooks and checking compensation limits..."
        })
        policy_task = await self._submit_handoff("policy", "Retrieve governing policies", {"evidence": evidence_step["result"]}, correlation_id, parent_task_id, "Evidence Agent")
        parent_task_id = policy_task.get("task_id")
        policy_step = await self.policy_agent.check_policies(evidence_step["result"], risk_result)
        await self._complete_handoff("policy", policy_task, policy_step["result"])
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
        recovery_task = await self._submit_handoff("recovery", "Prepare a draft-only recovery plan", {"order_id": order_id, "policy": policy_step["result"]}, correlation_id, parent_task_id, "Policy Retrieval Agent")
        parent_task_id = recovery_task.get("task_id")
        recovery_step = await self.recovery_agent.draft_recovery(order_data, evidence_step["result"], policy_step["result"])
        await self._complete_handoff("recovery", recovery_task, recovery_step["result"])
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
        guardrail_task = await self._submit_handoff("guardrail", "Apply deterministic safety validation", {"recovery": recovery_step["result"]}, correlation_id, parent_task_id, "Recovery Agent")
        guardrail_step = await self.guardrail_agent.validate(recovery_step["result"], policy_step["result"])
        await self._complete_handoff("guardrail", guardrail_task, guardrail_step["result"])
        traces.append(guardrail_step)
        await self._persist_trace(incident_id, order_id, guardrail_step)
        await ws_manager.broadcast({"type": "AGENT_STEP_COMPLETED", "trace": guardrail_step, "incident_id": incident_id})

        # Create Incident record in DB
        incident = IncidentModel(
            incident_id=incident_id,
            order_id=order_id,
            risk_level=risk_result["risk_level"],
            risk_score=risk_result["risk_score"],
            status="PENDING_REVIEW" if guardrail_step["result"]["passed_all_rules"] else "BLOCKED_HUMAN_REVIEW_REQUIRED",
            primary_risk_factor=risk_result["primary_risk_factor"],
            evidence_summary=evidence_step["result"]["evidence_summary"],
            recommended_action=recovery_step["result"]["action_brief"],
            guardrail_status=guardrail_step["result"]["guardrail_status"],
            guardrail_notes=guardrail_step["result"]["verdict"],
            proposed_action_type=recovery_step["result"]["action_type"],
            proposed_payload=recovery_step["result"],
            retrieved_sources=policy_step["result"].get("retrieved_sources", []),
            safety_checks=guardrail_step["result"].get("checks", []),
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
            thought=mask_pii(step_data.get("thought", "")),
            tool_name=step_data.get("tool_name"),
            tool_input=mask_pii(step_data.get("tool_input")),
            tool_output=mask_pii(step_data.get("tool_output")),
            latency_ms=step_data.get("latency_ms", 0),
            model_id=llm_provider.active_model,
            provider="AWS Bedrock",
            execution_mode=llm_provider.get_status()["execution_mode"],
            prompt_version="2026-09-v1",
            retrieved_source_ids=[source.get("source_id") for source in step_data.get("result", {}).get("retrieved_sources", [])],
        )
        self.db.add(trace)
        await self.db.commit()

    async def _submit_handoff(self, agent_id, goal, payload, correlation_id, parent_task_id, sender):
        if not self.a2a:
            return {"task_id": f"test-{agent_id}", "correlation_id": correlation_id, "status": "SUBMITTED"}
        return await self.a2a.submit(agent_id, goal, payload, correlation_id, parent_task_id, sender)

    async def _complete_handoff(self, agent_id, task, output):
        if self.a2a:
            await self.a2a.complete(agent_id, task["task_id"], output)
