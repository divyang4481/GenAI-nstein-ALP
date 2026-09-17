import asyncio
import datetime
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import select

from app.config import settings
from app.db import AsyncSessionLocal, OrderModel
from app.websocket import ws_manager
from app.agents.orchestrator import MultiAgentOrchestrator

logger = logging.getLogger("retailflow.replay")

class ReplayEngine:
    """Streams live Olist e-commerce order lifecycle events into the system."""

    def __init__(self):
        self.is_running = False
        self.interval_seconds = settings.REPLAY_INTERVAL_SECONDS
        self._task: Optional[asyncio.Task] = None
        self.current_event_index = 0

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())
            logger.info("Event replay engine started.")

    def pause(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Event replay engine paused.")

    def reset(self):
        self.pause()
        self.current_event_index = 0
        logger.info("Event replay engine reset to beginning.")

    def set_speed(self, interval_seconds: float):
        self.interval_seconds = max(0.2, min(10.0, interval_seconds))
        logger.info(f"Event replay interval set to {self.interval_seconds}s")

    async def _run_loop(self):
        while self.is_running:
            try:
                await self.trigger_next_event()
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in replay loop: {e}", exc_info=True)
                await asyncio.sleep(2.0)

    async def trigger_next_event(self) -> Optional[Dict[str, Any]]:
        async with AsyncSessionLocal() as db:
            res = await db.execute(select(OrderModel))
            orders: List[OrderModel] = res.scalars().all()
            if not orders:
                return None

            order = orders[self.current_event_index % len(orders)]
            self.current_event_index += 1

            # Determine synthetic event transition
            status_cycle = ["order_created", "seller_dispatched", "carrier_in_transit", "approaching_sla_risk"]
            event_type = status_cycle[self.current_event_index % len(status_cycle)]
            now_str = datetime.datetime.utcnow().strftime("%H:%M:%S")

            event_payload = {
                "event_id": f"EVT-{now_str.replace(':', '')}-{order.order_id[:6]}",
                "timestamp": now_str,
                "order_id": order.order_id,
                "customer_city": order.customer_city,
                "customer_state": order.customer_state,
                "seller_city": order.seller_city,
                "seller_state": order.seller_state,
                "carrier_name": order.carrier_name,
                "product_category": order.product_category_name,
                "event_type": event_type,
                "price": order.price,
                "is_at_risk": order.is_at_risk or (order.risk_score > settings.RISK_THRESHOLD_SCORE),
                "risk_score": order.risk_score
            }

            # Broadcast event to frontend
            await ws_manager.broadcast({
                "type": "ORDER_EVENT_EMITTED",
                "event": event_payload
            })

            # If order is high risk and in an approaching SLA state, launch multi-agent investigation
            if (order.is_at_risk or order.risk_score >= settings.RISK_THRESHOLD_SCORE) and event_type in ["carrier_in_transit", "approaching_sla_risk"]:
                # Run multi-agent investigation asynchronously
                asyncio.create_task(self._run_investigation_safely(order.order_id))

            return event_payload

    async def _run_investigation_safely(self, order_id: str):
        try:
            async with AsyncSessionLocal() as db:
                orchestrator = MultiAgentOrchestrator(db)
                await orchestrator.run_investigation(order_id)
        except Exception as e:
            logger.error(f"Error executing agent investigation for {order_id}: {e}", exc_info=True)

replay_engine = ReplayEngine()
