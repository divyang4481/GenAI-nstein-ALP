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
    orchestrator = MultiAgentOrchestrator(async_session)
    result = await orchestrator.run_investigation("8f3e2b4c1a5d0987654321fedcba9876")
    
    assert result["status"] == "INCIDENT_CREATED"
    assert len(result["traces"]) == 5  # 5 agents
    
    agent_names = [t["agent_name"] for t in result["traces"]]
    assert "Delivery-Risk Agent" in agent_names
    assert "Evidence Agent" in agent_names
    assert "Policy & RAG Agent" in agent_names
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
