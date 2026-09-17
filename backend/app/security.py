import re
from typing import Any

INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous instructions",
    r"reveal\s+(the\s+)?(system|hidden) prompt",
    r"override\s+(policy|guardrails?)",
    r"developer\s+message",
)


def contains_prompt_injection(value: str) -> bool:
    return any(re.search(pattern, value, re.I) for pattern in INJECTION_PATTERNS)


def mask_pii(value: Any) -> Any:
    """Recursively redact common contact, address and payment-shaped values."""
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if any(word in key.lower() for word in ("email", "phone", "address", "postal", "card", "payment")):
                result[key] = "***REDACTED***"
            else:
                result[key] = mask_pii(item)
        return result
    if isinstance(value, list):
        return [mask_pii(item) for item in value]
    if isinstance(value, str):
        value = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "***@***", value)
        value = re.sub(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)", "***REDACTED***", value)
    return value
