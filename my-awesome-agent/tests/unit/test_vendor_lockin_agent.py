import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.agents.vendor_lockin_agent import VendorLockinAgent
from app.models.vendor_risk import VendorLockinRisk
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig
from app.tools.vendor_tools import assess_vendor_lockin_risks

@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test")
    monkeypatch.setenv("BIGQUERY_DATASET", "ds")
    return PlatformConfig.from_env()

@pytest.fixture
def bq_service():
    return MagicMock(spec=BigQueryService)

def test_vendor_agent_persists_and_returns(config, bq_service):
    fake_risks = [
        VendorLockinRisk(
            service_name="S", cloud_provider="GCP", current_dependency_score=0.5,
            estimated_exit_cost_usd=1000, multi_cloud_feasibility="High",
            recommendation="Use Terraform", analysis_timestamp=datetime.utcnow().isoformat()
        )
    ]
    with patch("app.services.vendor_tools.assess_vendor_lockin_risks", return_value=fake_risks):
        agent = VendorLockinAgent(config, bq_service)
        results = agent.evaluate_lockin()

    assert results == fake_risks
    bq_service.insert_rows.assert_called_once()
    assert bq_service.insert_rows.call_args[0][0] == "vendor_risks"
