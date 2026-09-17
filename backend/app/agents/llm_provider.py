import asyncio
import importlib
import importlib.util
import json
import logging
from typing import Any, Dict, Optional

boto3 = importlib.import_module("boto3") if importlib.util.find_spec("boto3") else None

from app.config import settings

logger = logging.getLogger("retailflow.llm")


class LLMProvider:
    """Bedrock inference with an explicitly reported deterministic fallback."""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower()
        self.bedrock_model = settings.BEDROCK_MODEL
        self.aws_region = settings.AWS_REGION
        self.aws_profile = settings.AWS_PROFILE
        self.allowed_models = tuple(
            model.strip() for model in settings.BEDROCK_ALLOWED_MODELS.split(",") if model.strip()
        )
        if self.bedrock_model not in self.allowed_models:
            self.allowed_models = (self.bedrock_model, *self.allowed_models)
        self._bedrock_client = None
        self.ready = False
        self.last_successful_provider: Optional[str] = None
        self.last_error: Optional[str] = None
        self.fallback_active = True

    def _get_bedrock_client(self):
        if boto3 is None:
            raise RuntimeError("boto3 is unavailable; install backend/requirements.txt")
        if self._bedrock_client is None:
            session = None
            # 1. Try specified profile
            if self.aws_profile:
                try:
                    s = boto3.Session(profile_name=self.aws_profile)
                    if s.get_credentials() is not None:
                        session = s
                except Exception as e:
                    logger.debug("Boto3 profile session failed: %s", e)

            # 2. Try default credential chain (Env vars AWS_ACCESS_KEY_ID etc. or default profile)
            if session is None:
                try:
                    s = boto3.Session()
                    if s.get_credentials() is not None:
                        session = s
                except Exception as e:
                    logger.debug("Boto3 default session failed: %s", e)

            # 3. Fallback: Try AWS CLI credential export if aws CLI is available (e.g. for AWS SSO / aws login)
            if session is None and self.aws_profile:
                try:
                    import subprocess
                    out = subprocess.check_output(
                        ["aws", "configure", "export-credentials", "--profile", self.aws_profile],
                        timeout=5,
                        stderr=subprocess.DEVNULL
                    )
                    cred_data = json.loads(out.decode("utf-8"))
                    session = boto3.Session(
                        aws_access_key_id=cred_data.get("AccessKeyId"),
                        aws_secret_access_key=cred_data.get("SecretAccessKey"),
                        aws_session_token=cred_data.get("SessionToken"),
                        region_name=self.aws_region
                    )
                except Exception as e:
                    logger.debug("AWS CLI export-credentials fallback failed: %s", e)

            if session is None or session.get_credentials() is None:
                raise RuntimeError("AWS credentials were not found by the Boto3 credential chain")

            self._bedrock_client = session.client("bedrock-runtime", region_name=self.aws_region)
        return self._bedrock_client

    @property
    def active_model(self) -> str:
        return self.bedrock_model

    def validate_model(self, model_name: str) -> None:
        if model_name not in self.allowed_models:
            raise ValueError(f"Model '{model_name}' is not configured for this deployment")

    def get_status(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "active_model": self.active_model,
            "region": self.aws_region,
            "ready": self.ready,
            "execution_mode": "AWS_BEDROCK" if self.ready else "DETERMINISTIC_DEMO_FALLBACK",
            "last_successful_provider": self.last_successful_provider,
            "last_error": self.last_error,
            "fallback_active": self.fallback_active,
            "available_models": [
                {"id": model, "name": "Amazon Nova Lite" if "lite" in model else "Amazon Nova Pro", "provider": "bedrock"}
                for model in self.allowed_models
            ],
        }

    async def preflight_health_check(self) -> Dict[str, Any]:
        if self.provider != "bedrock":
            self.ready = False
            self.fallback_active = True
            self.last_error = "Only AWS Bedrock is supported as a cloud demo provider"
            return self.get_status()
        try:
            self.validate_model(self.bedrock_model)
            client = self._get_bedrock_client()
            payload = {
                "messages": [{"role": "user", "content": [{"text": "Reply with JSON: {\"ok\":true}"}]}],
                "inferenceConfig": {"max_new_tokens": 16, "temperature": 0},
            }
            await asyncio.to_thread(
                client.invoke_model,
                modelId=self.bedrock_model,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload),
            )
            self.ready = True
            self.fallback_active = False
            self.last_error = None
            self.last_successful_provider = "bedrock"
        except Exception as exc:
            self.ready = False
            self.fallback_active = True
            self.last_error = f"{type(exc).__name__}: {exc}"
            logger.warning("Bedrock preflight failed: %s", self.last_error)
        return self.get_status()

    async def generate_response(self, system_prompt: str, user_prompt: str, response_format: str = "json") -> Dict[str, Any]:
        if self.provider == "bedrock" and self.ready:
            try:
                payload = {
                    "system": [{"text": system_prompt + "\nRespond strictly in valid JSON."}],
                    "messages": [{"role": "user", "content": [{"text": user_prompt}]}],
                    "inferenceConfig": {"max_new_tokens": 400, "temperature": 0.1, "top_p": 0.9},
                }
                response = await asyncio.to_thread(
                    self._get_bedrock_client().invoke_model,
                    modelId=self.bedrock_model,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload),
                )
                body = json.loads(response["body"].read().decode("utf-8"))
                text = body.get("output", {}).get("message", {}).get("content", [{}])[0].get("text", "")
                parsed = self._extract_json(text) if response_format == "json" else None
                self.last_successful_provider = "bedrock"
                self.last_error = None
                self.fallback_active = False
                return parsed or {"text": text}
            except Exception as exc:
                self.ready = False
                self.fallback_active = True
                self.last_error = f"{type(exc).__name__}: {exc}"
                logger.error("Bedrock inference failed; deterministic fallback is active: %s", self.last_error)
        else:
            self.fallback_active = True
        return self._generate_simulated_agent_response(system_prompt, user_prompt)

    def _extract_json(self, raw_text: str) -> Optional[Dict[str, Any]]:
        """Cleans and extracts valid JSON even if wrapped in markdown code blocks."""
        cleaned = raw_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except Exception:
            # Try to find outermost curly braces
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(cleaned[start:end+1])
                except Exception:
                    pass
        return None

    def _generate_simulated_agent_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Provides high-fidelity, context-aware fallback responses."""
        prompt_lower = user_prompt.lower()
        
        if "risk" in system_prompt.lower() or "calculate delivery risk" in prompt_lower:
            return {
                "thought": "Assessing delivery risk based on order timeline, seller dispatch track record, and current carrier status.",
                "risk_score": 0.88 if ("curitiba" in prompt_lower or "8f3" in prompt_lower or "salvador" in prompt_lower) else 0.75,
                "risk_level": "CRITICAL" if ("curitiba" in prompt_lower or "8f3" in prompt_lower or "salvador" in prompt_lower) else "HIGH",
                "primary_risk_factor": "SLA deadline expiring in < 18 hours with interstate transit corridor bottleneck.",
                "sla_burn_rate_percent": 86.5,
                "recommended_investigation": "Deep dive into seller dispatch exceptions and active carrier transit ticket."
            }
        
        elif "evidence" in system_prompt.lower():
            return {
                "thought": "Queried seller historical dispatch rates and similar category incidents across the transit corridor.",
                "evidence_summary": "Order is at high risk. Seller has 3 recent delivery exceptions (17.0% late rate) and estimated delivery SLA is within 18 hours.",
                "key_findings": [
                    "Seller late order rate is 17.0% (industry average is 4%)",
                    "Hub transit queue experiencing severe weather/traffic delay",
                    "Customer order value is above category median"
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
                "executive_summary": "Order has high late-delivery risk. Its seller has recent delivery exceptions and estimated delivery date is within 18 hours. Recommend proactive courier escalation and customer update draft. Human approval required.",
                "proposed_voucher_brl": 20.00,
                "draft_customer_notification": "Olá! Your order is currently in transit. We noticed a brief transit hub delay and have expedited carrier priority. Revised ETA: Tomorrow by 18:00. We have attached a R$ 20.00 credit to your account.",
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
