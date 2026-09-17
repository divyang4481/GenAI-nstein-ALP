import time
from typing import Dict, Any
from app.agents.llm_provider import llm_provider
from app.guardrails import GuardrailEngine

class GuardrailAgent:
    """Enforces enterprise safety rules, responsible AI bounds, and human-in-the-loop validation."""

    def __init__(self, mcp_executor):
        self.mcp = mcp_executor
        self.name = "Enterprise Guardrail Agent"

    async def validate(self, recovery_data: Dict[str, Any], policy_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        
        system_prompt = (
            "You are the RetailFlow Enterprise Guardrail Agent. Audit the proposed recovery actions against "
            "Responsible AI guidelines: 1. No autonomous refunds 2. No direct customer communications without "
            "human signoff 3. Voucher compensation strictly <= policy limit. Output valid JSON."
        )
        user_prompt = (
            f"Proposed Recovery Plan: {recovery_data}\n"
            f"Policy Guardrails: {policy_data}"
        )
        
        llm_res = await llm_provider.generate_response(system_prompt, user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)
        
        deterministic = GuardrailEngine().validate(recovery_data, policy_data)

        return {
            "agent_name": self.name,
            "step_index": 5,
            "thought": "Applied deterministic safety checks; no private reasoning is stored.",
            "tool_name": None,
            "tool_input": None,
            "tool_output": None,
            "latency_ms": latency_ms,
            "result": {
                "guardrail_status": deterministic.status,
                "passed_all_rules": deterministic.allowed,
                "checks": deterministic.checks,
                "verdict": deterministic.verdict
            }
        }
