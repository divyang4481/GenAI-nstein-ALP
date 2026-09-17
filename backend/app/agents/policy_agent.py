import time
from typing import Dict, Any
from app.agents.llm_provider import llm_provider

class PolicyAgent:
    """RAG-grounded Policy Agent that checks governing SLAs, permitted playbooks, and compensation limits."""

    def __init__(self, mcp_executor):
        self.mcp = mcp_executor
        self.name = "Policy Retrieval Agent"

    async def check_policies(self, evidence_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        # Tool call: getPolicy (RAG lookup)
        query = f"{risk_data.get('risk_level')} delivery risk. {evidence_data.get('evidence_summary', '')} carrier escalation customer communication voucher"
        policies_res = await self.mcp.execute("retrieve_policy", {"query": query, "filters": {"source_type": "policy"}}, self.name)
        sources = policies_res.get("sources", [])
        if not sources:
            return {
                "agent_name": self.name, "step_index": 3,
                "thought": "No governing policy was retrieved; action proposal is fail-closed.",
                "tool_name": "retrieve_policy", "tool_input": {"query": query}, "tool_output": policies_res,
                "latency_ms": int((time.time() - start_time) * 1000),
                "result": {"applicable_policies": [], "permitted_actions": [], "prohibited_actions": ["ALL_EXTERNAL_ACTIONS"], "max_voucher_cap_brl": None, "requires_human_approval": True, "decision": "No governing policy found. Human review required. No action may be proposed.", "retrieved_sources": []},
            }
        
        system_prompt = (
            "You are the RetailFlow Policy Retrieval Agent. Match the incident against only the retrieved playbook chunks. "
            "Determine strictly permitted actions, maximum voucher compensation caps, and verify human approval requirements. "
            "Output valid JSON."
        )
        user_prompt = (
            "Use only retrieved evidence. If evidence is insufficient, say insufficient evidence.\n"
            f"<retrieved_policy_chunks>{sources}</retrieved_policy_chunks>\n\n"
            f"Incident Evidence:\n{evidence_data}\n\n"
            f"Risk Level:\n{risk_data}"
        )
        
        llm_res = await llm_provider.generate_response(system_prompt, user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "agent_name": self.name,
            "step_index": 3,
            "thought": llm_res.get("thought", "Checked corporate policy playbooks POL_CARRIER_ESCALATION_01 and POL_CUSTOMER_PROACTIVE_COMMS_02."),
            "tool_name": "retrieve_policy",
            "tool_input": {"query": query, "filters": {"source_type": "policy"}},
            "tool_output": policies_res,
            "latency_ms": latency_ms,
            "result": {
                "applicable_policies": list(dict.fromkeys(source.get("policy_id") for source in sources if source.get("policy_id"))),
                "permitted_actions": llm_res.get("permitted_actions", ["ESCALATE_CARRIER_PRIORITY", "DRAFT_CUSTOMER_UPDATE", "OFFER_GOODWILL_VOUCHER_MAX_25_BRL"]),
                "prohibited_actions": llm_res.get("prohibited_actions", ["AUTO_FULL_REFUND", "CANCEL_IN_FLIGHT_SHIPMENT"]),
                "max_voucher_cap_brl": max([source.get("metadata", {}).get("max_voucher_brl", 0.0) for source in sources] or [0.0]),
                "requires_human_approval": True,
                "retrieved_sources": sources
            }
        }
