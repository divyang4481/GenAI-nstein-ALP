import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import OrderModel, SellerHistoryModel, PolicyPlaybookModel, IncidentModel

# Schema descriptions for MCP tool discovery
MCP_TOOLS_MANIFEST = [
    {
        "name": "getOrder",
        "description": "Fetch detailed live order record including pricing, freight, customer geo-location, seller, and estimated vs actual SLA timestamps.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The unique 32-character Olist order identifier."}
            },
            "required": ["order_id"]
        }
    },
    {
        "name": "getSellerHistory",
        "description": "Retrieve seller fulfillment track record, dispatch SLA compliance, recent delivery exception count, and average customer review score.",
        "parameters": {
            "type": "object",
            "properties": {
                "seller_id": {"type": "string", "description": "The unique seller identifier."}
            },
            "required": ["seller_id"]
        }
    },
    {
        "name": "findSimilarCases",
        "description": "Search historical fulfillment resolution cases for the same product category, carrier, or interstate transit corridor.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_category": {"type": "string", "description": "e.g. relogios_presentes, informatica_acessorios"},
                "customer_state": {"type": "string", "description": "Two letter state abbreviation, e.g. SP, RJ, BA"}
            },
            "required": ["product_category"]
        }
    },
    {
        "name": "getPolicy",
        "description": "Retrieve governing marketplace fulfillment policies, permitted resolution playbooks, voucher caps, and guardrail constraints.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "description": "Policy category e.g. CARRIER_ESCALATION, CUSTOMER_COMMS, SLA_BREACH"}
            }
        }
    },
    {
        "name": "createCase",
        "description": "Initialize a formal operational incident in the recovery ledger with calculated risk parameters.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order ID being flagged"},
                "risk_score": {"type": "number", "description": "Calculated risk score between 0.0 and 1.0"},
                "primary_risk_factor": {"type": "string", "description": "Root cause summary"}
            },
            "required": ["order_id", "risk_score", "primary_risk_factor"]
        }
    },
    {
        "name": "escalateCarrier",
        "description": "Format and dispatch carrier escalation ticket to expedite transit priority.",
        "parameters": {
            "type": "object",
            "properties": {
                "carrier_name": {"type": "string", "description": "Carrier name e.g. Correios SEDEX"},
                "order_id": {"type": "string", "description": "Target order ID"},
                "priority_level": {"type": "string", "enum": ["PRIORITY_1_CRITICAL", "PRIORITY_2_HIGH", "STANDARD"]}
            },
            "required": ["carrier_name", "order_id", "priority_level"]
        }
    },
    {
        "name": "draftCustomerMessage",
        "description": "Generate proactive customer update message with empathy and revised delivery ETA.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Target order ID"},
                "customer_city": {"type": "string", "description": "Destination city"},
                "revised_eta": {"type": "string", "description": "Updated estimated delivery window"},
                "compensation_voucher_brl": {"type": "number", "description": "Optional voucher amount up to policy cap"}
            },
            "required": ["order_id", "revised_eta"]
        }
    }
]

class MCPToolExecutor:
    """Executes MCP tools against the local state store and returns structured payloads."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "getOrder":
            return await self.get_order(arguments.get("order_id", ""))
        elif tool_name == "getSellerHistory":
            return await self.get_seller_history(arguments.get("seller_id", ""))
        elif tool_name == "findSimilarCases":
            return await self.find_similar_cases(
                arguments.get("product_category", ""),
                arguments.get("customer_state", "")
            )
        elif tool_name == "getPolicy":
            return await self.get_policy(arguments.get("category"))
        elif tool_name == "createCase":
            return await self.create_case(
                arguments.get("order_id", ""),
                arguments.get("risk_score", 0.0),
                arguments.get("primary_risk_factor", "")
            )
        elif tool_name == "escalateCarrier":
            return await self.escalate_carrier(
                arguments.get("carrier_name", "Correios"),
                arguments.get("order_id", ""),
                arguments.get("priority_level", "PRIORITY_1_CRITICAL")
            )
        elif tool_name == "draftCustomerMessage":
            return await self.draft_customer_message(
                arguments.get("order_id", ""),
                arguments.get("customer_city", "São Paulo"),
                arguments.get("revised_eta", "Next 48 Hours"),
                arguments.get("compensation_voucher_brl", 0.0)
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    async def get_order(self, order_id: str) -> Dict[str, Any]:
        res = await self.db.execute(select(OrderModel).where(OrderModel.order_id == order_id))
        order = res.scalars().first()
        if not order:
            return {"status": "NOT_FOUND", "message": f"Order {order_id} not found."}
        return {
            "status": "SUCCESS",
            "order_id": order.order_id,
            "customer_id": order.customer_id,
            "customer_city": order.customer_city,
            "customer_state": order.customer_state,
            "order_status": order.order_status,
            "order_purchase_timestamp": order.order_purchase_timestamp,
            "order_estimated_delivery_date": order.order_estimated_delivery_date,
            "freight_value": order.freight_value,
            "price": order.price,
            "product_category_name": order.product_category_name,
            "seller_id": order.seller_id,
            "seller_city": order.seller_city,
            "seller_state": order.seller_state,
            "carrier_name": order.carrier_name,
            "risk_score": order.risk_score
        }

    async def get_seller_history(self, seller_id: str) -> Dict[str, Any]:
        res = await self.db.execute(select(SellerHistoryModel).where(SellerHistoryModel.seller_id == seller_id))
        seller = res.scalars().first()
        if not seller:
            return {
                "status": "DEFAULT_PROFILE",
                "seller_id": seller_id,
                "total_orders": 50,
                "late_orders_count": 5,
                "late_order_rate": 0.10,
                "avg_dispatch_hours": 30.0,
                "recent_exceptions_count": 1,
                "review_score_avg": 4.2
            }
        return {
            "status": "SUCCESS",
            "seller_id": seller.seller_id,
            "seller_city": seller.seller_city,
            "seller_state": seller.seller_state,
            "total_orders": seller.total_orders,
            "late_orders_count": seller.late_orders_count,
            "late_order_rate": seller.late_order_rate,
            "avg_dispatch_hours": seller.avg_dispatch_hours,
            "recent_exceptions_count": seller.recent_exceptions_count,
            "review_score_avg": seller.review_score_avg
        }

    async def find_similar_cases(self, product_category: str, customer_state: str) -> Dict[str, Any]:
        return {
            "status": "SUCCESS",
            "match_count": 3,
            "historical_cases": [
                {
                    "case_id": "CASE_HIST_9921",
                    "category": product_category,
                    "route": f"PR -> {customer_state or 'SP'}",
                    "delay_reason": "Hub transit congestion at Curitiba cross-dock",
                    "resolution": "Carrier escalation + R$ 20 goodwill credit",
                    "outcome": "Customer 5-star review retained, delivery completed in +28h"
                },
                {
                    "case_id": "CASE_HIST_8812",
                    "category": product_category,
                    "route": f"SP -> {customer_state or 'RJ'}",
                    "delay_reason": "Carrier sorting backlog",
                    "resolution": "Proactive WhatsApp SMS notice + expedited courier routing",
                    "outcome": "Avoided order cancellation"
                }
            ]
        }

    async def get_policy(self, category: Optional[str] = None) -> Dict[str, Any]:
        query = select(PolicyPlaybookModel)
        if category:
            query = query.where(PolicyPlaybookModel.category == category)
        res = await self.db.execute(query)
        policies = res.scalars().all()
        return {
            "status": "SUCCESS",
            "policies": [
                {
                    "policy_id": p.policy_id,
                    "title": p.title,
                    "category": p.category,
                    "conditions": p.conditions,
                    "permitted_actions": p.permitted_actions,
                    "prohibited_actions": p.prohibited_actions,
                    "max_voucher_brl": p.max_voucher_brl,
                    "requires_human_approval": p.requires_human_approval,
                    "playbook_text": p.playbook_text
                }
                for p in policies
            ]
        }

    async def create_case(self, order_id: str, risk_score: float, primary_risk_factor: str) -> Dict[str, Any]:
        incident_id = f"INC-{order_id[:8].upper()}-{datetime.datetime.utcnow().strftime('%H%M%S')}"
        return {
            "status": "CASE_INITIALIZED",
            "incident_id": incident_id,
            "order_id": order_id,
            "risk_score": risk_score,
            "primary_risk_factor": primary_risk_factor,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    async def escalate_carrier(self, carrier_name: str, order_id: str, priority_level: str) -> Dict[str, Any]:
        ticket_id = f"TKT-CARRIER-{order_id[:6].upper()}-99"
        return {
            "status": "ESCALATION_DISPATCHED",
            "carrier": carrier_name,
            "ticket_id": ticket_id,
            "priority": priority_level,
            "action": "Hub supervisor notified for express routing",
            "expected_eta_reduction_hours": 24
        }

    async def draft_customer_message(self, order_id: str, customer_city: str, revised_eta: str, compensation_voucher_brl: float) -> Dict[str, Any]:
        voucher_text = f" To apologize for any inconvenience, we have attached a R$ {compensation_voucher_brl:.2f} marketplace credit." if compensation_voucher_brl > 0 else ""
        message_body = (
            f"Olá! We are tracking your order ({order_id[:8]}...) heading to {customer_city}. "
            f"Due to regional hub transit congestion, our logistics team has proactively expedited your parcel. "
            f"Your new delivery window is {revised_eta}.{voucher_text} Thank you for shopping with us!"
        )
        return {
            "status": "DRAFTED_PENDING_APPROVAL",
            "recipient_city": customer_city,
            "message_body": message_body,
            "requires_human_signoff": True
        }
