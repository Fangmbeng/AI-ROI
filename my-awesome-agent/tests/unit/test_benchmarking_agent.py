import pytest
from unittest.mock import MagicMock
from datetime import datetime

from app.agents.benchmarking_agent import BenchmarkingAgent
from app.models.benchmark import BenchmarkResult
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
def bq_service():
    return MagicMock(spec=BigQueryService)

@pytest.fixture
def vertex_service():
    svc = MagicMock(spec=VertexAIService)
    svc.generate_benchmark_comparisons.return_value = [
        {
            "benchmark_type": "Model",
            "entity_name": "X",
            "baseline_name": "Y",
            "performance_score": 0.9,
            "baseline_score": 0.8,
            "metric": "Accuracy",
            "score_unit": "score",
            "deviation": 12.5,
            "comment": "Test"
        }
    ]
    return svc

def test_benchmarking_agent_persists_and_returns(config, bq_service, vertex_service):
    agent = BenchmarkingAgent(config, bq_service, vertex_service)
    results = agent.benchmark_ai_systems()

    assert all(isinstance(r, BenchmarkResult) for r in results)
    assert len(results) == 1

    vertex_service.generate_benchmark_comparisons.assert_called_once()

    # Verify persistence
    assert bq_service.insert_rows.call_count == 1
    table, rows = bq_service.insert_rows.call_args[0]
    assert table == "benchmarks"
    assert rows[0]["entity_name"] == "X"
