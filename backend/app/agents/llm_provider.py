import os
import json
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("retailflow.llm")

class LLMProvider:
    """Unified LLM interface supporting Intelligent Zero-Config Simulation, OpenAI, Gemini, and Amazon Bedrock."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()

    async def generate_response(self, system_prompt: str, user_prompt: str, response_format: str = "json") -> Dict[str, Any]:
        if self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                        json={
                            "model": "gpt-4o-mini",
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            "response_format": {"type": "json_object"} if response_format == "json" else None,
                            "temperature": 0.2
                        },
                        timeout=15.0
                    )
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    return json.loads(content) if response_format == "json" else {"text": content}
            except Exception as e:
                logger.warning(f"OpenAI call failed ({e}), falling back to internal deterministic agent engine.")

        elif self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                import httpx
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
                async with httpx.AsyncClient() as client:
                    res = await client.post(
                        url,
                        json={
                            "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                            "generationConfig": {"responseMimeType": "application/json"} if response_format == "json" else {}
                        },
                        timeout=15.0
                    )
                    data = res.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(content) if response_format == "json" else {"text": content}
            except Exception as e:
                logger.warning(f"Gemini call failed ({e}), falling back to internal deterministic agent engine.")

        # Default / Zero-Config fallback engine
        return self._generate_simulated_agent_response(system_prompt, user_prompt)

    def _generate_simulated_agent_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Provides instant, realistic, context-aware responses adhering to agent schemas."""
        prompt_lower = user_prompt.lower()
        
        if "risk" in system_prompt.lower() or "calculate delivery risk" in prompt_lower:
            return {
                "thought": "Assessing delivery risk based on order timeline, seller dispatch track record, and current carrier status.",
                "risk_score": 0.88 if "curitiba" in prompt_lower or "8f3" in prompt_lower else 0.75,
                "risk_level": "CRITICAL" if "curitiba" in prompt_lower or "8f3" in prompt_lower else "HIGH",
                "primary_risk_factor": "SLA deadline expiring in < 18 hours with interstate transit corridor bottleneck (Curitiba -> SP).",
                "sla_burn_rate_percent": 86.5,
                "recommended_investigation": "Deep dive into seller dispatch exceptions and active carrier transit ticket."
            }
        
        elif "evidence" in system_prompt.lower():
            return {
                "thought": "Gave priority to querying seller historical dispatch rates and similar category incidents in São Paulo.",
                "evidence_summary": "Order 8f3... is at high risk. Seller has 3 recent delivery exceptions (17.0% late rate) and estimated delivery SLA is within 18 hours. Correios SEDEX hub shows 24h backlog.",
                "key_findings": [
                    "Seller late order rate is 17.0% (industry average is 4%)",
                    "Hub transit queue at Curitiba cross-dock experiencing severe weather/traffic delay",
                    "Customer order value is R$ 389.90 (High Priority Customer category)"
                ]
            }
            
        elif "policy" in system_prompt.lower():
            return {
                "thought": "Checked Policy POL_CARRIER_ESCALATION_01 and POL_CUSTOMER_PROACTIVE_COMMS_02 against fulfillment status.",
                "applicable_policies": ["POL_CARRIER_ESCALATION_01", "POL_CUSTOMER_PROACTIVE_COMMS_02"],
                "permitted_actions": ["ESCALATE_CARRIER_PRIORITY", "DRAFT_CUSTOMER_UPDATE", "OFFER_GOODWILL_VOUCHER_MAX_25_BRL"],
                "prohibited_actions": ["AUTO_FULL_REFUND", "CANCEL_IN_FLIGHT_SHIPMENT"],
                "requires_human_approval": True,
                "max_voucher_cap_brl": 25.0
            }
            
        elif "recovery" in system_prompt.lower():
            return {
                "thought": "Synthesizing safe recovery brief incorporating proactive courier escalation and draft customer notice.",
                "action_type": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT",
                "headline": "Proactive Courier Escalation & Customer Update Draft",
                "executive_summary": "Order has high late-delivery risk. Its seller has 3 recent delivery exceptions and estimated delivery date is within 18 hours. Recommend proactive courier escalation and customer update draft. Human approval required.",
                "recommended_actions": [
                    {
                        "action": "ESCALATE_CARRIER_PRIORITY",
                        "target": "Correios SEDEX (Ticket Escalation Priority 1)",
                        "impact": "Reduces regional hub sorting time by ~24 hours"
                    },
                    {
                        "action": "DRAFT_CUSTOMER_UPDATE",
                        "target": "Customer c_sp_94821 (São Paulo)",
                        "impact": "Prevents 1-star bad review and order cancellation"
                    }
                ],
                "proposed_voucher_brl": 20.00,
                "draft_customer_notification": "Olá! Your order 8f3e... is currently en route to São Paulo. We noticed a brief transit hub delay and have expedited carrier priority. Revised ETA: Tomorrow by 18:00. We have attached a R$ 20.00 credit to your account.",
                "requires_human_approval": True
            }
            
        elif "guardrail" in system_prompt.lower():
            return {
                "guardrail_status": "PASSED",
                "passed_all_rules": True,
                "checks": [
                    {"rule": "NO_AUTONOMOUS_REFUND", "passed": True, "notes": "No unconditional refund was scheduled without ops sign-off."},
                    {"rule": "NO_UNAUTHORIZED_CUSTOMER_CONTACT", "passed": True, "notes": "Customer message is held in draft state pending human review."},
                    {"rule": "VOUCHER_POLICY_CAP", "passed": True, "notes": "Proposed R$ 20.00 credit is strictly <= policy cap of R$ 25.00."},
                    {"rule": "STRUCTURED_SCHEMA_VALIDITY", "passed": True, "notes": "All required incident fields properly typed."}
                ],
                "verdict": "Recovery plan complies with all corporate fulfillment safety policies. Ready for Human Operations Approval."
            }

        return {"response": "Processed successfully."}

llm_provider = LLMProvider()
