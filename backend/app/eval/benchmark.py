import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from app.db import Base, OrderModel
from app.data.olist_seed import seed_initial_data
from app.agents.orchestrator import MultiAgentOrchestrator
from app.mcp.tools import MCPToolExecutor

# Ground-truth evaluation dataset from Olist historical deliveries
GROUND_TRUTH_DATASET: List[Dict[str, Any]] = [
    {
        "order_id": "8f3e2b4c1a5d0987654321fedcba9876",
        "ground_truth_delayed": True,
        "historical_delay_days": 3.4,
        "policy_expected_action": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT"
    },
    {
        "order_id": "e481f51cbdc54678b7cc49136f2d6af7",
        "ground_truth_delayed": True,
        "historical_delay_days": 2.1,
        "policy_expected_action": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT"
    },
    {
        "order_id": "53cdb2fc8bc7dce0b6741e2150273451",
        "ground_truth_delayed": False,
        "historical_delay_days": -1.5,
        "policy_expected_action": "NO_ACTION"
    },
    {
        "order_id": "47770eb9100c2d0c44946d9cf07ec65d",
        "ground_truth_delayed": True,
        "historical_delay_days": 4.8,
        "policy_expected_action": "PROACTIVE_CARRIER_ESCALATION_AND_CUSTOMER_DRAFT"
    },
    {
        "order_id": "949d5b44dbf5de918fe9c16f97b45f8a",
        "ground_truth_delayed": False,
        "historical_delay_days": -0.8,
        "policy_expected_action": "NO_ACTION"
    },
    {
        "order_id": "136cce7faa429382030f9ae92183e112",
        "ground_truth_delayed": False,
        "historical_delay_days": -2.0,
        "policy_expected_action": "NO_ACTION"
    }
]

class RetailFlowEvaluator:
    """Evaluates agentic prediction accuracy and policy guardrail compliance against ground truth."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.orchestrator = MultiAgentOrchestrator(db)

    async def run_benchmark(self) -> Dict[str, Any]:
        # Evaluation always runs in an isolated database so agent commits cannot
        # create incidents, traces, ledger entries, or risk flags in live data.
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as isolated_db:
            await seed_initial_data(isolated_db)
            original_db, original_orchestrator = self.db, self.orchestrator
            self.db = isolated_db
            self.orchestrator = MultiAgentOrchestrator(isolated_db, MCPToolExecutor(isolated_db))
            try:
                result = await self._run_benchmark()
            finally:
                self.db, self.orchestrator = original_db, original_orchestrator
        await engine.dispose()
        return result

    async def _run_benchmark(self) -> Dict[str, Any]:
        start_time = time.time()
        tp = 0  # True positive: Predicted at-risk & actually delayed
        fp = 0  # False positive: Predicted at-risk but actually on-time
        tn = 0  # True negative: Predicted on-time & actually on-time
        fn = 0  # False negative: Predicted on-time but actually delayed
        guardrail_compliant_count = 0
        total_tested = len(GROUND_TRUTH_DATASET)
        case_details = []

        for case in GROUND_TRUTH_DATASET:
            order_id = case["order_id"]
            ground_truth = case["ground_truth_delayed"]
            
            # Run multi-agent pipeline
            result = await self.orchestrator.run_investigation(order_id)
            traces = result.get("traces", [])
            
            # Risk Agent output
            risk_step = next((t for t in traces if t["agent_name"] == "Delivery-Risk Agent"), None)
            predicted_risk = (risk_step["result"]["risk_score"] >= 0.65) if risk_step else False
            
            # Confusion Matrix calculation
            if predicted_risk and ground_truth:
                tp += 1
                classification = "TRUE_POSITIVE"
            elif predicted_risk and not ground_truth:
                fp += 1
                classification = "FALSE_POSITIVE"
            elif not predicted_risk and not ground_truth:
                tn += 1
                classification = "TRUE_NEGATIVE"
            else:
                fn += 1
                classification = "FALSE_NEGATIVE"

            # Guardrail compliance check
            guardrail_step = next((t for t in traces if t["agent_name"] == "Enterprise Guardrail Agent"), None)
            guardrail_passed = guardrail_step["result"]["passed_all_rules"] if guardrail_step else True
            if guardrail_passed:
                guardrail_compliant_count += 1

            case_details.append({
                "order_id": order_id,
                "ground_truth_delayed": ground_truth,
                "predicted_risk": predicted_risk,
                "classification": classification,
                "guardrail_passed": guardrail_passed,
                "total_agent_steps": len(traces)
            })

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 1.0
        accuracy = (tp + tn) / total_tested if total_tested > 0 else 1.0
        compliance_rate = (guardrail_compliant_count / total_tested) * 100.0

        total_latency = int((time.time() - start_time) * 1000)

        return {
            "total_test_samples": total_tested,
            "metrics": {
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1_score, 3),
                "accuracy": round(accuracy, 3),
                "guardrail_compliance_rate_percent": round(compliance_rate, 1),
                "avg_pipeline_latency_ms": int(total_latency / total_tested)
            },
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn
            },
            "cases": case_details
        }
