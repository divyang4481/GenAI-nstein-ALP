from typing import Literal
from pydantic import BaseModel, Field


class RiskNarrative(BaseModel):
    risk_score: float = Field(ge=0, le=1)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    primary_risk_factor: str


class EvidenceBrief(BaseModel):
    evidence_summary: str
    key_findings: list[str] = []


class PolicyDecision(BaseModel):
    applicable_policies: list[str]
    permitted_actions: list[str]
    prohibited_actions: list[str]
    max_voucher_cap_brl: float | None = Field(default=None, ge=0)
    requires_human_approval: bool = True


class RecoveryPlan(BaseModel):
    action_type: str
    executive_summary: str
    proposed_voucher_brl: float = Field(ge=0)
    draft_customer_notification: str
    requires_human_approval: bool = True


class CaseAnswer(BaseModel):
    answer: str
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    grounded: bool
