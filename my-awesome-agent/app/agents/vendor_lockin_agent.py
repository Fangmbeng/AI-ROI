# app/agents/vendor_lockin_agent.py

from typing import List
from datetime import datetime
from vertexai.preview.reasoning_engines import LangchainAgent
from google.adk.agents import LlmAgent

from app.models.vendor_risk import VendorLockinRisk
from app.tools.vendor_tools import assess_vendor_lockin_risks
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig

class VendorLockinAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, bq_service: BigQueryService):

        super().__init__(
            name="vendor_lockin_agent",
            model="gemini-2.0-flash",
            description="Assesses vendor lock-in risk, persists risk assessments",
            tools=[self.evaluate_lockin],
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

    def evaluate_lockin(self) -> List[VendorLockinRisk]:
        risks = assess_vendor_lockin_risks()
        ts = datetime.utcnow().isoformat()
        rows = []
        for r in risks:
            rows.append({
                "timestamp": ts,
                "service_name": r.service_name,
                "cloud_provider": r.cloud_provider,
                "current_dependency_score": r.current_dependency_score,
                "estimated_exit_cost_usd": r.estimated_exit_cost_usd,
                "multi_cloud_feasibility": r.multi_cloud_feasibility,
                "recommendation": r.recommendation
            })
        self.bq.insert_rows("vendor_risks", rows)
        return risks
