from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

from app.security import contains_prompt_injection

ALLOWED_ACTIONS = {
    "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT",
    "CARRIER_ESCALATION_DRAFT",
    "CUSTOMER_MESSAGE_DRAFT",
    "VOUCHER_DRAFT",
}


@dataclass
class GuardrailResult:
    allowed: bool
    status: str
    checks: list[dict[str, str]]
    verdict: str


class GuardrailEngine:
    """Deterministic safety authority. Model output is never used to waive a rule."""

    def validate(self, recovery: dict[str, Any], policy: dict[str, Any], user_input: str = "") -> GuardrailResult:
        checks: list[dict[str, str]] = []

        def check(name: str, passed: bool, detail: str) -> None:
            checks.append({"rule_name": name, "status": "PASSED" if passed else "FAILED", "description": detail})

        injection_safe = not contains_prompt_injection(user_input)
        check("PROMPT_INJECTION_DEFENCE", injection_safe, "Override/hidden-prompt requests are rejected.")

        action_type = recovery.get("action_type")
        check("SUPPORTED_DRAFT_ACTION", action_type in ALLOWED_ACTIONS, "Only supported draft action types are accepted.")
        check("HUMAN_APPROVAL_REQUIRED", recovery.get("requires_human_approval") is True, "External effects require an authorised reviewer.")
        check("CUSTOMER_MESSAGE_REMAINS_DRAFT", recovery.get("send_customer_message") is not True, "No customer delivery endpoint is available.")

        cap = policy.get("max_voucher_cap_brl")
        amount = recovery.get("proposed_voucher_brl", 0)
        try:
            voucher = Decimal(str(amount))
            maximum = Decimal(str(cap)) if cap is not None else None
            voucher_ok = voucher >= 0 and maximum is not None and voucher <= maximum
        except (InvalidOperation, ValueError, TypeError):
            voucher_ok = False
        check("VOUCHER_POLICY_CAP", voucher_ok, "Voucher must be numeric, non-negative and no greater than a retrieved policy cap.")

        policies = policy.get("applicable_policies") or []
        check("GOVERNING_POLICY_PRESENT", bool(policies), "At least one retrieved policy citation is required.")
        currency_ok = recovery.get("voucher_currency", "BRL") == "BRL"
        check("SUPPORTED_CURRENCY", currency_ok, "The MVP supports BRL vouchers only.")

        allowed = all(item["status"] == "PASSED" for item in checks)
        return GuardrailResult(
            allowed=allowed,
            status="PASSED" if allowed else "BLOCKED_HUMAN_REVIEW_REQUIRED",
            checks=checks,
            verdict="Ready for human review." if allowed else "Blocked — human review required.",
        )
