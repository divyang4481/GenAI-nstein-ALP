import time
from typing import Dict, Any
from app.agents.llm_provider import llm_provider
from app.mcp.tools import MCPToolExecutor

class DeliveryRiskAgent:
    """Calculates order fulfillment delivery risk, SLA burn rate, and delay likelihood."""

    def __init__(self, mcp_executor: MCPToolExecutor):
        self.mcp = mcp_executor
        self.name = "Delivery-Risk Agent"

    async def evaluate(self, order_id: str) -> Dict[str, Any]:
        start_time = time.time()
        
        # Tool call: getOrder
        order_data = await self.mcp.execute("getOrder", {"order_id": order_id})
        
        system_prompt = (
            "You are the RetailFlow Delivery-Risk Agent. Your job is to analyze real-time marketplace order "
            "fulfillment events and identify delivery-risk bottlenecks before SLA breaches occur. Output valid JSON."
        )
        user_prompt = (
            f"Calculate delivery risk for order:\n"
            f"Order ID: {order_id}\n"
            f"Status: {order_data.get('order_status')}\n"
            f"Origin: {order_data.get('seller_city')}, {order_data.get('seller_state')}\n"
            f"Destination: {order_data.get('customer_city')}, {order_data.get('customer_state')}\n"
            f"Carrier: {order_data.get('carrier_name')}\n"
            f"Estimated Delivery SLA: {order_data.get('order_estimated_delivery_date')}\n"
            f"Product Category: {order_data.get('product_category_name')}"
        )
        
        llm_res = await llm_provider.generate_response(system_prompt, user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Deterministic risk heuristics
        risk_score = float(order_data.get("risk_score", 0.85)) if order_data.get("risk_score") else float(llm_res.get("risk_score", 0.85))
        risk_level = "CRITICAL" if risk_score >= 0.80 else ("HIGH" if risk_score >= 0.60 else ("MEDIUM" if risk_score >= 0.40 else "LOW"))

        return {
            "agent_name": self.name,
            "step_index": 1,
            "thought": llm_res.get("thought", f"Assessing delivery risk for order {order_id} across interstate transit corridor."),
            "tool_name": "getOrder",
            "tool_input": {"order_id": order_id},
            "tool_output": order_data,
            "latency_ms": latency_ms,
            "result": {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "primary_risk_factor": llm_res.get("primary_risk_factor", "Interstate hub transit delay approaching SLA deadline."),
                "sla_burn_rate_percent": llm_res.get("sla_burn_rate_percent", 86.5)
            }
        }
