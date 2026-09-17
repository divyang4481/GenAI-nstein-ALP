import os
from typing import Any

from fastapi import Request
from mcp.server.fastmcp import FastMCP
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import OrderModel, SellerHistoryModel
from app.retrieval import retrieval_service

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./retailflow.db")
SERVICE_TOKEN = os.getenv("MCP_SERVICE_TOKEN", "local-development-token")
engine = create_async_engine(DATABASE_URL)
Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
mcp = FastMCP("RetailFlow Tools", host="0.0.0.0", port=8001, stateless_http=True)


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request):
    from starlette.responses import JSONResponse
    return JSONResponse({"status": "healthy", "transport": "MCP Streamable HTTP"})


@mcp.tool()
async def get_order(order_id: str) -> dict[str, Any]:
    """Get one historical replay order. Contact and payment values are not returned."""
    async with Session() as db:
        order = (await db.execute(select(OrderModel).where(OrderModel.order_id == order_id))).scalars().first()
        if not order:
            return {"status": "NOT_FOUND", "order_id": order_id}
        return {column.name: getattr(order, column.name) for column in OrderModel.__table__.columns if column.name not in {"customer_id"}}


@mcp.tool()
async def get_seller_history(seller_id: str) -> dict[str, Any]:
    """Get aggregate seller fulfilment history."""
    async with Session() as db:
        seller = (await db.execute(select(SellerHistoryModel).where(SellerHistoryModel.seller_id == seller_id))).scalars().first()
        if not seller:
            return {"status": "NOT_FOUND", "seller_id": seller_id}
        return {column.name: getattr(seller, column.name) for column in SellerHistoryModel.__table__.columns}


@mcp.tool()
async def find_similar_cases(category: str, customer_state: str) -> dict[str, Any]:
    """Retrieve semantically similar historical cases from Qdrant."""
    sources = await retrieval_service.search(f"{category} {customer_state} delivery delay", source_type="historical_case")
    return {"status": "SUCCESS", "historical_cases": [source.public_dict() for source in sources]}


@mcp.tool()
async def retrieve_policy(query: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
    """Retrieve governing policy chunks from Qdrant, never the whole policy store."""
    sources = await retrieval_service.search(query, source_type="policy")
    return {"status": "SUCCESS", "sources": [source.public_dict() for source in sources]}


@mcp.tool()
async def create_recovery_draft(order_id: str, action_payload: dict[str, Any]) -> dict[str, Any]:
    """Create a draft payload only. This tool has no external connector capability."""
    return {"status": "DRAFT", "order_id": order_id, "action_payload": action_payload, "requires_human_approval": True}


if __name__ == "__main__":
    import uvicorn

    class TokenMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http" and scope.get("path", "").startswith("/mcp"):
                headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
                if headers.get("authorization") != f"Bearer {SERVICE_TOKEN}":
                    await send({"type": "http.response.start", "status": 401, "headers": [(b"content-type", b"application/json")]})
                    await send({"type": "http.response.body", "body": b'{"detail":"invalid service token"}'})
                    return
            await self.app(scope, receive, send)

    uvicorn.run(TokenMiddleware(mcp.streamable_http_app()), host="0.0.0.0", port=8001)
