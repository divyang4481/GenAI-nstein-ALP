import datetime
from typing import AsyncGenerator
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

Base = declarative_base()
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

class OrderModel(Base):
    __tablename__ = "orders"

    order_id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(String(64), index=True)
    customer_city = Column(String(64))
    customer_state = Column(String(8))
    order_status = Column(String(32), default="created")  # created, approved, seller_dispatched, in_transit, delivered, delayed, cancelled
    order_purchase_timestamp = Column(String(32))
    order_estimated_delivery_date = Column(String(32))
    order_delivered_customer_date = Column(String(32), nullable=True)
    freight_value = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    product_category_name = Column(String(64))
    seller_id = Column(String(64), index=True)
    seller_city = Column(String(64))
    seller_state = Column(String(8))
    carrier_name = Column(String(64), default="Correios SEDEX")
    review_score = Column(Integer, nullable=True)
    is_at_risk = Column(Boolean, default=False)
    risk_score = Column(Float, default=0.0)
    last_event_time = Column(DateTime, default=datetime.datetime.utcnow)

class SellerHistoryModel(Base):
    __tablename__ = "seller_history"

    seller_id = Column(String(64), primary_key=True, index=True)
    seller_city = Column(String(64))
    seller_state = Column(String(8))
    total_orders = Column(Integer, default=100)
    late_orders_count = Column(Integer, default=12)
    late_order_rate = Column(Float, default=0.12)
    avg_dispatch_hours = Column(Float, default=36.0)
    recent_exceptions_count = Column(Integer, default=3)
    review_score_avg = Column(Float, default=4.1)

class IncidentModel(Base):
    __tablename__ = "incidents"

    incident_id = Column(String(64), primary_key=True, index=True)
    order_id = Column(String(64), index=True)
    risk_level = Column(String(16))  # CRITICAL, HIGH, MEDIUM, LOW
    risk_score = Column(Float)
    status = Column(String(32), default="PENDING_REVIEW")  # PENDING_REVIEW, APPROVED, REJECTED, AUTO_RESOLVED
    primary_risk_factor = Column(String(256))
    evidence_summary = Column(Text)
    recommended_action = Column(Text)
    guardrail_status = Column(String(32), default="PASSED")
    guardrail_notes = Column(Text)
    proposed_action_type = Column(String(64))
    proposed_payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_decision = Column(String(32), nullable=True)  # APPROVED, REJECTED
    reviewer_notes = Column(Text, nullable=True)

class AgentTraceModel(Base):
    __tablename__ = "agent_traces"

    trace_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), index=True)
    order_id = Column(String(64), index=True)
    agent_name = Column(String(64))  # Delivery-Risk, Evidence, Policy, Recovery, Guardrail
    step_index = Column(Integer)
    thought = Column(Text)
    tool_name = Column(String(64), nullable=True)
    tool_input = Column(JSON, nullable=True)
    tool_output = Column(JSON, nullable=True)
    latency_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ActionLedgerModel(Base):
    __tablename__ = "action_ledger"

    action_id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), index=True)
    order_id = Column(String(64), index=True)
    action_type = Column(String(64))  # CARRIER_ESCALATION, REROUTE_3PL, CUSTOMER_PROACTIVE_UPDATE, VOUCHER_CREDIT
    status = Column(String(32), default="EXECUTED")  # EXECUTED, REJECTED, CANCELLED
    payload = Column(JSON)
    proposed_by = Column(String(64), default="RetailFlow Recovery Agent")
    approved_by = Column(String(64), default="Human Ops Supervisor")
    executed_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text)

class PolicyPlaybookModel(Base):
    __tablename__ = "policy_playbooks"

    policy_id = Column(String(64), primary_key=True, index=True)
    title = Column(String(128))
    category = Column(String(64))  # CARRIER_ESCALATION, COMPENSATION, CUSTOMER_COMMS, SLA_BREACH
    conditions = Column(Text)
    permitted_actions = Column(JSON)
    prohibited_actions = Column(JSON)
    max_voucher_brl = Column(Float, default=30.0)
    requires_human_approval = Column(Boolean, default=True)
    playbook_text = Column(Text)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
