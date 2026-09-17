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
        customer_state = order_data.get("customer_state", "SP")
        seller_state = order_data.get("seller_state", "SP")
        category = order_data.get("product_category_name", "item").replace("_", " ")
        price = float(order_data.get("price") or 100.0)
        
        # Determine dynamic goodwill voucher based on order value tier and policy cap
        policy_cap = float(policy_data.get("max_voucher_cap_brl") or 25.0)
        if price >= 500.0:
            suggested_voucher = min(policy_cap, 30.0 if policy_cap >= 30.0 else policy_cap)
        elif price >= 150.0:
            suggested_voucher = min(policy_cap, 20.0)
        else:
            suggested_voucher = min(policy_cap, 15.0)
        suggested_voucher = round(max(0.0, suggested_voucher), 2)

        # Dynamic revised ETA based on interstate vs intrastate corridor
        if seller_state != customer_state:
            revised_eta = "48h buffer (Interstate corridor priority)"
            delay_impact = "Reduces interstate line-haul delay by ~24-48h"
        else:
            revised_eta = "Tomorrow by 18:00 (Local metro hub)"
            delay_impact = "Expedites regional distribution hub dispatch by ~24h"

        draft = await self.mcp.execute("create_recovery_draft", {"order_id": order_id, "action_payload": {
            "action_type": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT",
            "carrier_name": carrier,
            "customer_city": city,
            "revised_eta": revised_eta,
            "proposed_voucher_brl": suggested_voucher,
        }}, self.name)
        carrier_escalation_draft = draft
        customer_message_draft = {
            "status": "DRAFT",
            "message_body": (
                f"Customer notification draft: Proactive update regarding your {category} order to {city}, {customer_state}. "
                f"We expedited dispatch via {carrier} ({revised_eta}) and credited R$ {suggested_voucher:.2f} store credit."
            )
        }
        
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
            f"Order {order_id[:8]}... has high late-delivery risk on route {seller_state} -> {customer_state}. "
            f"Recommend proactive courier escalation with {carrier} ({revised_eta}) and "
            f"a customer retention update with R$ {suggested_voucher:.2f} goodwill credit. Human approval required."
        )

        return {
            "agent_name": self.name,
            "step_index": 4,
            "thought": llm_res.get("thought", f"Synthesized recovery brief with {carrier} escalation and R$ {suggested_voucher:.2f} customer voucher."),
            "tool_name": "draftCustomerMessage",
            "tool_input": {"order_id": order_id, "voucher": suggested_voucher},
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
                        "impact": delay_impact
                    },
                    {
                        "action_id": "ACT_02",
                        "name": "Customer Communication & Goodwill Credit",
                        "target": f"Customer in {city}, {customer_state}",
                        "impact": f"Retains customer trust with R$ {suggested_voucher:.2f} retention credit"
                    }
                ],
                "proposed_voucher_brl": suggested_voucher,
                "draft_message": customer_message_draft.get("message_body"),
                "requires_human_approval": True
            }
        }
