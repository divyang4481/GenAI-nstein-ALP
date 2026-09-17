import time
import uuid
import importlib
import importlib.util
import json
from typing import Any

ClientSession = importlib.import_module("mcp").ClientSession if importlib.util.find_spec("mcp") else None
_stream_mod = importlib.import_module("mcp.client.streamable_http") if ClientSession else None
streamablehttp_client = (
    getattr(_stream_mod, "streamable_http_client", None) or getattr(_stream_mod, "streamablehttp_client", None)
    if _stream_mod else None
)

from app.config import settings

MCP_TOOLS_MANIFEST = [
    {"name": "get_order", "description": "Read one historical replay order", "inputSchema": {"type": "object", "required": ["order_id"], "properties": {"order_id": {"type": "string"}}}},
    {"name": "get_seller_history", "description": "Read aggregate seller fulfilment history", "inputSchema": {"type": "object", "required": ["seller_id"], "properties": {"seller_id": {"type": "string"}}}},
    {"name": "find_similar_cases", "description": "Retrieve similar historical cases from Qdrant", "inputSchema": {"type": "object", "required": ["category", "customer_state"], "properties": {"category": {"type": "string"}, "customer_state": {"type": "string"}}}},
    {"name": "retrieve_policy", "description": "Retrieve governing policy chunks from Qdrant", "inputSchema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "filters": {"type": "object"}}}},
    {"name": "create_recovery_draft", "description": "Create a draft only; never execute an external action", "inputSchema": {"type": "object", "required": ["order_id", "action_payload"], "properties": {"order_id": {"type": "string"}, "action_payload": {"type": "object"}}}},
]


class MCPClient:
    """A real MCP Streamable HTTP client; it never imports server tool functions."""

    TOOL_ALLOWLIST = {
        "Delivery-Risk Agent": {"get_order"},
        "Evidence Agent": {"get_seller_history", "find_similar_cases"},
        "Policy Retrieval Agent": {"retrieve_policy"},
        "Recovery Agent": {"create_recovery_draft"},
    }
    LEGACY_NAMES = {
        "getOrder": "get_order", "getSellerHistory": "get_seller_history",
        "findSimilarCases": "find_similar_cases", "getPolicy": "retrieve_policy",
        "escalateCarrier": "create_recovery_draft", "draftCustomerMessage": "create_recovery_draft",
    }

    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.url = (base_url or settings.MCP_SERVER_URL).rstrip("/") + "/mcp"
        self.headers = {"Authorization": f"Bearer {token or settings.MCP_SERVICE_TOKEN}"}
        self.invocations: list[dict[str, Any]] = []

    async def execute(self, tool_name: str, arguments: dict[str, Any], agent_name: str | None = None) -> dict[str, Any]:
        canonical = self.LEGACY_NAMES.get(tool_name, tool_name)
        if agent_name and canonical not in self.TOOL_ALLOWLIST.get(agent_name, set()):
            raise PermissionError(f"{agent_name} is not allowed to call {canonical}")
        invocation_id = str(uuid.uuid4())
        started = time.perf_counter()
        status = "FAILED"
        try:
            if ClientSession is None or streamablehttp_client is None:
                raise RuntimeError("The MCP SDK is required for service transport; install backend/requirements.txt")
            import httpx
            async with httpx.AsyncClient(headers=self.headers) as http_client:
                async with streamablehttp_client(self.url, http_client=http_client) as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.call_tool(canonical, arguments=arguments)
            if result.isError:
                raise RuntimeError(str(result.content))
            structured = result.structuredContent
            if structured is None and result.content:
                structured = getattr(result.content[0], "text", "")
                if isinstance(structured, str):
                    structured = json.loads(structured)
            status = "SUCCESS"
            return structured if isinstance(structured, dict) else {"result": structured}
        finally:
            self.invocations.append({
                "invocation_id": invocation_id, "tool_name": canonical,
                "request": arguments, "duration_ms": int((time.perf_counter() - started) * 1000), "status": status,
            })
