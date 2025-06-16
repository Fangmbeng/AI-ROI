# app/agents/infrastructure_cost_agent.py
from datetime import timedelta, datetime
from typing import List, Dict
from vertexai.preview.reasoning_engines import ReasoningEngine, LangchainAgent
from app.services.gcp_billing_service import GCPBillingService
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig
from app.models.infrastructure_data import InfrastructureCostData
from google.adk.agents import LlmAgent


class InfrastructureCostAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, bq_service: BigQueryService):

        super().__init__(
            name="infrastructure_cost_agent",
            model="gemini-2.0-flash",
            description="Monitors real-time infrastructure costs and persists metrics",
            tools=[
                self.get_gcp_costs,
                self.get_total_cost_summary,
            ],
        )

        object.__setattr__(self, '_config', config)
        object.__setattr__(self, '_bq', bq_service)
        object.__setattr__(self, '_billing', GCPBillingService(config))

    @property
    def billing(self):
        return self._billing

    @property
    def bq(self):
        return self._bq

    @property
    def config(self):
        return self._config
    
    def get_gcp_costs(self) -> List[InfrastructureCostData]:
        records = self.billing.get_detailed_billing_data(
            self.billing.project_id,
            (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
            datetime.utcnow().strftime("%Y-%m-%d")
        )
        # Map to table schema and insert
        rows = [
            {
                'timestamp': r['date'],
                'project_id': self.billing.project_id,
                'service_name': r['service'],
                'resource_type': 'N/A',
                'cost_usd': r['cost'],
                'usage_amount': r['usage'],
                'usage_unit': r['unit'],
                'region': None,
                'metadata': {}
            }
            for r in records
        ]
        self.bq.insert_rows('infrastructure_metrics', rows)
        return [InfrastructureCostData(**r) for r in records]

    def get_total_cost_summary(self) -> Dict[str, float]:
        summary = self.billing.aggregate_by_service(
            self.billing.get_detailed_billing_data(
                self.billing.project_id,
                (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
                datetime.utcnow().strftime("%Y-%m-%d")
            )
        )
        return summary
