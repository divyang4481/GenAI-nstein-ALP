import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db import Base, OrderModel, SellerHistoryModel, PolicyPlaybookModel
from app.data.olist_seed import seed_initial_data
from app.agents.orchestrator import MultiAgentOrchestrator
from app.mcp.tools import MCPToolExecutor

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with SessionLocal() as session:
        await seed_initial_data(session)
        yield session

@pytest.mark.asyncio
async def test_mcp_tools(async_session: AsyncSession):
    mcp = MCPToolExecutor(async_session)
    order_res = await mcp.execute("getOrder", {"order_id": "8f3e2b4c1a5d0987654321fedcba9876"})
    assert order_res["status"] == "SUCCESS"
    assert order_res["customer_state"] == "SP"
    assert order_res["seller_state"] == "PR"

    seller_res = await mcp.execute("getSellerHistory", {"seller_id": "s_curitiba_4021"})
    assert seller_res["status"] == "SUCCESS"
    assert seller_res["recent_exceptions_count"] == 3

    policy_res = await mcp.execute("getPolicy", {})
    assert policy_res["status"] == "SUCCESS"
    assert len(policy_res["policies"]) >= 3

@pytest.mark.asyncio
async def test_multi_agent_pipeline_execution(async_session: AsyncSession):
    orchestrator = MultiAgentOrchestrator(async_session, MCPToolExecutor(async_session))
    result = await orchestrator.run_investigation("8f3e2b4c1a5d0987654321fedcba9876")
    
    assert result["status"] == "INCIDENT_CREATED"
    assert len(result["traces"]) == 5  # 5 agents
    
    agent_names = [t["agent_name"] for t in result["traces"]]
    assert "Delivery-Risk Agent" in agent_names
    assert "Evidence Agent" in agent_names
    assert "Policy Retrieval Agent" in agent_names
    assert "Recovery Agent" in agent_names
    assert "Enterprise Guardrail Agent" in agent_names
    
    # Verify guardrail passed
    guardrail_step = result["traces"][4]
    assert guardrail_step["result"]["guardrail_status"] == "PASSED"
    assert guardrail_step["result"]["passed_all_rules"] is True

@pytest.mark.asyncio
async def test_evaluator_benchmark(async_session: AsyncSession):
    from app.eval.benchmark import RetailFlowEvaluator
    evaluator = RetailFlowEvaluator(async_session)
    bench = await evaluator.run_benchmark()
    
    assert bench["total_test_samples"] == 6
    assert bench["metrics"]["precision"] >= 0.80
    assert bench["metrics"]["guardrail_compliance_rate_percent"] == 100.0

@pytest.mark.asyncio
async def test_bedrock_preflight_and_response_with_mocked_client(monkeypatch):
    import io
    import json
    from app.agents import llm_provider as provider_module

    class FakeClient:
        def invoke_model(self, **kwargs):
            assert kwargs["modelId"] == "us.amazon.nova-lite-v1:0"
            return {"body": io.BytesIO(json.dumps({"output": {"message": {"content": [{"text": '{"ok": true}'}]}}}).encode())}

    class FakeSession:
        def __init__(self, profile_name=None):
            assert profile_name in (None, "retailflow-demo")
        def get_credentials(self):
            return object()
        def client(self, service, region_name=None):
            assert service == "bedrock-runtime"
            return FakeClient()

    monkeypatch.setattr(provider_module, "boto3", type("FakeBoto", (), {"Session": FakeSession}))
    provider = provider_module.LLMProvider()
    provider.bedrock_model = "us.amazon.nova-lite-v1:0"
    status = await provider.preflight_health_check()
    assert status["ready"] is True
    assert status["execution_mode"] == "AWS_BEDROCK"
    assert status["fallback_active"] is False

@pytest.mark.asyncio
async def test_invalid_decision_is_rejected(async_session: AsyncSession):
    from fastapi import HTTPException
    from app.main import submit_human_decision

    with pytest.raises(HTTPException) as error:
        await submit_human_decision("missing", {"decision": "AUTO_RESOLVED"}, async_session)
    assert error.value.status_code == 422

@pytest.mark.asyncio
async def test_duplicate_pending_incident_is_prevented(async_session: AsyncSession):
    orchestrator = MultiAgentOrchestrator(async_session, MCPToolExecutor(async_session))
    first = await orchestrator.run_investigation("8f3e2b4c1a5d0987654321fedcba9876")
    second = await orchestrator.run_investigation("8f3e2b4c1a5d0987654321fedcba9876")
    assert second["status"] == "PENDING_INCIDENT_EXISTS"
    assert second["incident_id"] == first["incident_id"]

@pytest.mark.asyncio
async def test_evaluation_does_not_change_live_incidents(async_session: AsyncSession):
    from sqlalchemy import func, select
    from app.db import IncidentModel
    from app.eval.benchmark import RetailFlowEvaluator

    before = (await async_session.execute(select(func.count(IncidentModel.incident_id)))).scalar()
    await RetailFlowEvaluator(async_session).run_benchmark()
    after = (await async_session.execute(select(func.count(IncidentModel.incident_id)))).scalar()
    assert after == before

@pytest.mark.asyncio
async def test_demo_reset_clears_generated_records_and_reseeds(async_session: AsyncSession):
    from sqlalchemy import func, select
    from app.db import ActionLedgerModel, AgentTraceModel, IncidentModel, OrderModel
    from app.main import reset_replay

    await MultiAgentOrchestrator(async_session, MCPToolExecutor(async_session)).run_investigation("8f3e2b4c1a5d0987654321fedcba9876")
    assert (await async_session.execute(select(func.count(IncidentModel.incident_id)))).scalar() == 1
    result = await reset_replay(async_session)
    assert result == {"status": "RESET"}
    assert (await async_session.execute(select(func.count(IncidentModel.incident_id)))).scalar() == 0
    assert (await async_session.execute(select(func.count(AgentTraceModel.trace_id)))).scalar() == 0
    assert (await async_session.execute(select(func.count(ActionLedgerModel.action_id)))).scalar() == 0
    assert (await async_session.execute(select(func.count(OrderModel.order_id)))).scalar() > 0

@pytest.mark.asyncio
async def test_api_happy_path(async_session: AsyncSession):
    import httpx
    from app.db import get_db
    from app.main import app

    async def override_db():
        yield async_session

    app.dependency_overrides[get_db] = override_db
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            orders = await client.get("/api/orders")
            status = await client.get("/api/llm/status")
        assert orders.status_code == 200
        assert len(orders.json()) > 0
        assert status.status_code == 200
        assert "execution_mode" in status.json()
    finally:
        app.dependency_overrides.clear()
