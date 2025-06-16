import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.agents.carbon_tracking_agent import CarbonTrackingAgent
from app.models.carbon import CarbonFootprint
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.utils.config import PlatformConfig

@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-proj")
    monkeypatch.setenv("BIGQUERY_DATASET", "ds")
    return PlatformConfig.from_env()

@pytest.fixture
def bq_service():
    return MagicMock(spec=BigQueryService)

@pytest.fixture
def vertex_service():
    svc = MagicMock(spec=VertexAIService)
    svc.calculate_carbon_emissions.return_value = {"total_kg_co2e": 200.0, "scope_3_included": True}
    return svc

def test_carbon_agent_persists_and_returns(config, bq_service, vertex_service):
    agent = CarbonTrackingAgent(config, vertex_service, bq_service)
    results = agent.track_carbon()

    assert all(isinstance(r, CarbonFootprint) for r in results)
    assert results[0].estimated_kg_co2e == 200.0

    vertex_service.calculate_carbon_emissions.assert_called_once()
    bq_service.insert_rows.assert_called_once()
    assert bq_service.insert_rows.call_args[0][0] == "carbon_metrics"
