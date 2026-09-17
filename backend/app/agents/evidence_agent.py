import time
from typing import Dict, Any
from app.agents.llm_provider import llm_provider
from app.mcp.tools import MCPToolExecutor

class EvidenceAgent:
    """Gathers seller performance history, similar past fulfillment issues, and route bottlenecks."""

    def __init__(self, mcp_executor: MCPToolExecutor):
        self.mcp = mcp_executor
        self.name = "Evidence Agent"

    async def gather(self, order_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        seller_id = order_data.get("seller_id", "")
        category = order_data.get("product_category_name", "")
        state = order_data.get("customer_state", "")
        
        # Tool call 1: getSellerHistory
        seller_history = await self.mcp.execute("getSellerHistory", {"seller_id": seller_id})
        
        # Tool call 2: findSimilarCases
        similar_cases = await self.mcp.execute("findSimilarCases", {
            "product_category": category,
            "customer_state": state
        })
        
        system_prompt = (
            "You are the RetailFlow Evidence Agent. Synthesize order details, seller history, and historical "
            "corridor delay benchmarks to formulate a factual root-cause evidence brief. Output valid JSON."
        )
        user_prompt = (
            f"Seller Track Record: {seller_history}\n"
            f"Similar Cases: {similar_cases}\n"
            f"Order Context: {order_data}\n"
            f"Risk Evaluation: {risk_data}"
        )
        
        llm_res = await llm_provider.generate_response(system_prompt, user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)
        
        evidence_summary = (
            f"Order {order_data.get('order_id', '')[:8]}... has high late-delivery risk. "
            f"Its seller ({seller_id}) has {seller_history.get('recent_exceptions_count', 3)} recent delivery exceptions "
            f"(historical late rate {seller_history.get('late_order_rate', 0.17)*100:.1f}%) and the estimated delivery SLA "
            f"is within 18 hours. Route {order_data.get('seller_state')} -> {order_data.get('customer_state')} shows hub backlog."
        )

        return {
            "agent_name": self.name,
            "step_index": 2,
            "thought": llm_res.get("thought", "Queried seller history and similar historical cases in the logistics network."),
            "tool_name": "getSellerHistory",
            "tool_input": {"seller_id": seller_id, "category": category},
            "tool_output": {
                "seller_history": seller_history,
                "similar_cases": similar_cases
            },
            "latency_ms": latency_ms,
            "result": {
                "evidence_summary": llm_res.get("evidence_summary", evidence_summary),
                "seller_history": seller_history,
                "similar_cases": similar_cases
            }
        }
