import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.agents.forecasting_agent import ForecastingAgent
from app.models.forecast import Forecast
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.utils.config import PlatformConfig

@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-proj")
    monkeypatch.setenv("BIGQUERY_DATASET", "ds")
    monkeypatch.setenv("VERTEX_AI_LOCATION", "us-central1")
    return PlatformConfig.from_env()

@pytest.fixture
def bq_service(config):
    svc = MagicMock(spec=BigQueryService)
    return svc

@pytest.fixture
def vertex_service(config):
    svc = MagicMock(spec=VertexAIService)
    # Return two dummy forecasts
    svc.forecast_infrastructure_needs.return_value = [
        {"resource": "vCPU", "forecast": 100, "unit": "count"},
        {"resource": "TPU",  "forecast":  10, "unit": "count"},
    ]
    return svc

def test_forecasting_agent_persists_and_returns(config, bq_service, vertex_service):
    agent = ForecastingAgent(config, bq_service, vertex_service)
    results = agent.predict_ai_infra_trends()

    # Validate return type
    assert all(isinstance(r, Forecast) for r in results)
    assert len(results) == 2

    # Ensure we called the vertex service
    vertex_service.forecast_infrastructure_needs.assert_called_once()

    # Ensure we persisted two rows
    assert bq_service.insert_rows.call_count == 1
    table_name, rows = bq_service.insert_rows.call_args[0]
    assert table_name == "forecasts"
    assert len(rows) == 2
    # Check row shape
    for row in rows:
        assert "timestamp" in row and "forecast_value" in row
