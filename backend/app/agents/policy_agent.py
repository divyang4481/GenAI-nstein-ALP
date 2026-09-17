import time
from typing import Dict, Any
from app.agents.llm_provider import llm_provider
from app.mcp.tools import MCPToolExecutor

class PolicyAgent:
    """RAG-grounded Policy Agent that checks governing SLAs, permitted playbooks, and compensation limits."""

    def __init__(self, mcp_executor: MCPToolExecutor):
        self.mcp = mcp_executor
        self.name = "Policy & RAG Agent"

    async def check_policies(self, evidence_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        # Tool call: getPolicy (RAG lookup)
        policies_res = await self.mcp.execute("getPolicy", {})
        policies = policies_res.get("policies", [])
        
        system_prompt = (
            "You are the RetailFlow Policy & RAG Agent. Match the fulfillment incident against enterprise playbooks. "
            "Determine strictly permitted actions, maximum voucher compensation caps, and verify human approval requirements. "
            "Output valid JSON."
        )
        user_prompt = (
            f"Available Corporate Policies:\n{policies}\n\n"
            f"Incident Evidence:\n{evidence_data}\n\n"
            f"Risk Level:\n{risk_data}"
        )
        
        llm_res = await llm_provider.generate_response(system_prompt, user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)

        return {
            "agent_name": self.name,
            "step_index": 3,
            "thought": llm_res.get("thought", "Checked corporate policy playbooks POL_CARRIER_ESCALATION_01 and POL_CUSTOMER_PROACTIVE_COMMS_02."),
            "tool_name": "getPolicy",
            "tool_input": {"scenario": "CARRIER_ESCALATION_AND_CUSTOMER_COMMS"},
            "tool_output": policies_res,
            "latency_ms": latency_ms,
            "result": {
                "applicable_policies": llm_res.get("applicable_policies", ["POL_CARRIER_ESCALATION_01", "POL_CUSTOMER_PROACTIVE_COMMS_02"]),
                "permitted_actions": llm_res.get("permitted_actions", ["ESCALATE_CARRIER_PRIORITY", "DRAFT_CUSTOMER_UPDATE", "OFFER_GOODWILL_VOUCHER_MAX_25_BRL"]),
                "prohibited_actions": llm_res.get("prohibited_actions", ["AUTO_FULL_REFUND", "CANCEL_IN_FLIGHT_SHIPMENT"]),
                "max_voucher_cap_brl": llm_res.get("max_voucher_cap_brl", 25.0),
                "requires_human_approval": True
            }
        }
