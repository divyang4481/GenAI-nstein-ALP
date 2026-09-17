import time
from typing import Dict, Any
from app.agents.llm_provider import llm_provider

class RecoveryAgent:
    """Formulates a multi-action recovery plan and prepares an executive action brief for human review."""

    def __init__(self, mcp_executor):
        self.mcp = mcp_executor
        self.name = "Recovery Agent"

    async def draft_recovery(self, order_data: Dict[str, Any], evidence_data: Dict[str, Any], policy_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        order_id = order_data.get("order_id", "")
        carrier = order_data.get("carrier_name", "Correios SEDEX")
        city = order_data.get("customer_city", "São Paulo")
        
        draft = await self.mcp.execute("create_recovery_draft", {"order_id": order_id, "action_payload": {
            "action_type": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT", "carrier_name": carrier,
            "customer_city": city, "revised_eta": "Tomorrow by 18:00", "proposed_voucher_brl": 20.0,
        }}, self.name)
        carrier_escalation_draft = draft
        customer_message_draft = {"status": "DRAFT", "message_body": "Customer delivery update draft; no message has been sent."}
        
        system_prompt = (
            "You are the RetailFlow Recovery Agent. Formulate a recovery plan brief for the human operations team. "
            "Follow the exact corporate action structure. Output valid JSON."
        )
        user_prompt = (
            f"Order Context: {order_data}\n"
            f"Evidence: {evidence_data}\n"
            f"Permitted Policies: {policy_data}\n"
            f"Carrier Escalation Draft: {carrier_escalation_draft}\n"
            f"Customer Message Draft: {customer_message_draft}"
        )
        
        llm_res = await llm_provider.generate_response(system_prompt, user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)

        action_brief = (
            f"Order {order_id[:8]}... has high late-delivery risk. Its seller has 3 recent delivery exceptions "
            f"and the estimated delivery date is within 18 hours. Recommend proactive courier escalation and "
            f"a customer-update draft. Human approval required."
        )

        return {
            "agent_name": self.name,
            "step_index": 4,
            "thought": llm_res.get("thought", "Synthesized recovery brief with courier escalation and customer update."),
            "tool_name": "draftCustomerMessage",
            "tool_input": {"order_id": order_id, "voucher": 20.00},
            "tool_output": {
                "carrier_escalation": carrier_escalation_draft,
                "customer_message": customer_message_draft
            },
            "latency_ms": latency_ms,
            "result": {
                "action_type": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT",
                "action_brief": llm_res.get("executive_summary", action_brief),
                "proposed_actions": [
                    {
                        "action_id": "ACT_01",
                        "name": "Proactive Carrier Escalation",
                        "target": f"{carrier} (Priority 1 Expedited Hub)",
                        "impact": "Reduces regional transit sorting delay by ~24h"
                    },
                    {
                        "action_id": "ACT_02",
                        "name": "Customer Communication & R$ 20 Credit",
                        "target": f"Customer in {city}",
                        "impact": "Prevents 1-star review and retains customer trust"
                    }
                ],
                "proposed_voucher_brl": 20.00,
                "draft_message": customer_message_draft.get("message_body"),
                "requires_human_approval": True
            }
        }
