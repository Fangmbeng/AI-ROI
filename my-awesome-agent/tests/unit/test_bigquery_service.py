# tests/unit/test_bigquery_service.py

import pytest
from unittest.mock import MagicMock, patch
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig

@pytest.fixture
def fake_config(tmp_path, monkeypatch):
    # Minimal env vars for PlatformConfig
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")
    monkeypatch.setenv("BIGQUERY_DATASET", "test_dataset")
    return PlatformConfig.from_env()

@patch("app.services.bigquery_service.bigquery.Client")
def test_insert_and_fetch(mock_bq_client_cls, fake_config):
    # Mock client and table
    mock_client = MagicMock()
    mock_bq_client_cls.return_value = mock_client

    service = BigQueryService(fake_config)

    # Prepare fake rows and ensure no errors on insert
    mock_client.insert_rows_json.return_value = []
    rows = [{"timestamp": "2025-06-01T00:00:00Z", "project_id": "test", "service_name": "S", "resource_type": "R", "cost_usd": 10.0}]
    service.insert_rows("infrastructure_metrics", rows)
    mock_client.insert_rows_json.assert_called_once()

    # Mock query to return a DataFrame-like with to_dict on fetch
    fake_df = MagicMock()
    fake_df.to_dict.return_value = [{"metric_name": "X", "metric_value": 42.0}]
    mock_client.query.return_value.to_dataframe.return_value = fake_df

    result = service.fetch_business_metrics("7d", metrics_filter=["X"])
    assert isinstance(result, list)
    assert result == [{"metric_name": "X", "metric_value": 42.0}]

@patch("app.services.bigquery_service.bigquery.Client")
def test_calculate_custom_kpis(mock_bq_client_cls, fake_config):
    mock_client = MagicMock()
    mock_bq_client_cls.return_value = mock_client

    service = BigQueryService(fake_config)
    # Mock dataframe
    fake_df = MagicMock()
    fake_df.to_dict.return_value = [{"metric_name": "A", "metric_value": 1.23}]
    mock_client.query.return_value.to_dataframe.return_value = fake_df

    custom = service.calculate_custom_kpis(["A"])
    assert custom == [{"metric_name": "A", "metric_value": 1.23}]
