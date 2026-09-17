import uuid
from typing import Any

import httpx

from app.config import settings


class A2AGateway:
    """HTTP task-envelope gateway used for every agent handoff."""

    def __init__(self, base_url: str | None = None, token: str | None = None):
        self.base_url = (base_url or settings.A2A_BASE_URL).rstrip("/")
        self.headers = {"Authorization": f"Bearer {token or settings.MCP_SERVICE_TOKEN}"}

    async def submit(self, agent_id: str, goal: str, input_payload: dict[str, Any], correlation_id: str, parent_task_id: str | None, sender: str) -> dict[str, Any]:
        envelope = {
            "task_id": str(uuid.uuid4()), "correlation_id": correlation_id, "parent_task_id": parent_task_id,
            "sender_agent": sender, "task_goal": goal, "input_schema_version": "1.0",
            "output_schema_version": "1.0", "input": input_payload,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{self.base_url}/agents/{agent_id}/tasks", json=envelope, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def complete(self, agent_id: str, task_id: str, output_payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.patch(f"{self.base_url}/agents/{agent_id}/tasks/{task_id}", json={"status": "COMPLETED", "output": output_payload}, headers=self.headers)
            response.raise_for_status()
            return response.json()
