# app/agents/security_compliance_agent.py

from typing import List
from datetime import datetime
from vertexai.preview.reasoning_engines import ReasoningEngine, LangchainAgent
from google.adk.agents import LlmAgent

from app.models.compliance import ComplianceFinding
from app.tools.compliance_tool import scan_compliance_violations
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig

class SecurityComplianceAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, bq_service: BigQueryService):

        super().__init__(
            name="security_compliance_agent",
            model="gemini-2.0-flash",
            description="Audits security and compliance, persists findings",
            tools=[self.audit_compliance],
        )

        # Initialize services using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_config', config)
        object.__setattr__(self, '_bq', bq_service)

    @property
    def bq(self):
        return self._bq

    @property
    def config(self):
        return self._config

    def audit_compliance(self) -> List[ComplianceFinding]:
        findings = scan_compliance_violations()
        ts = datetime.utcnow().isoformat()
        rows = []
        for f in findings:
            rows.append({
                "timestamp": ts,
                "check_name": f.check_name,
                "resource": f.resource,
                "status": f.status,
                "severity": f.severity,
                "description": f.description,
                "remediation": f.remediation
            })
        self.bq.insert_rows("compliance_findings", rows)
        return findings
