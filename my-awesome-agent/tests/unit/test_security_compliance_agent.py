import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.agents.security_compliance_agent import SecurityComplianceAgent
from app.models.compliance import ComplianceFinding
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig
from app.tools.compliance_tools import scan_compliance_violations

@pytest.fixture
def config(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test")
    monkeypatch.setenv("BIGQUERY_DATASET", "ds")
    return PlatformConfig.from_env()

@pytest.fixture
def bq_service():
    return MagicMock(spec=BigQueryService)

def test_security_agent_persists_and_returns(config, bq_service):
    fake_findings = [
        ComplianceFinding(
            check_name="X", resource="R", status="FAIL", severity="High",
            description="D", remediation="Fix", timestamp=datetime.utcnow().isoformat()
        )
    ]
    with patch("app.services.compliance_tools.scan_compliance_violations", return_value=fake_findings):
        agent = SecurityComplianceAgent(config, bq_service)
        results = agent.audit_compliance()

    assert results == fake_findings
    bq_service.insert_rows.assert_called_once()
    assert bq_service.insert_rows.call_args[0][0] == "compliance_findings"
