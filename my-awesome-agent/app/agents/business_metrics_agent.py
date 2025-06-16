# app/agents/business_metrics_agent.py

from typing import List
from vertexai.preview.reasoning_engines import LangchainAgent
from google.adk.agents import LlmAgent

from app.services.integration_service import CRMIntegration, ERPIntegration, FinancialIntegration
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig
from app.models.business_metrics import BusinessKPIData


class BusinessMetricsAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, bq_service: BigQueryService):
        # Call parent constructor first
        super().__init__(
            name="business_metrics_agent",
            description="Extracts and provides business KPIs from CRM, ERP, and financial systems",
            tools=[
                self.get_revenue_kpis,
                self.get_customer_kpis,
                self.get_operational_kpis,
                self.get_financials,
            ],
        )
        
        # Initialize services using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_crm', CRMIntegration(system=config.crm_system))
        object.__setattr__(self, '_erp', ERPIntegration(system=config.erp_system))
        object.__setattr__(self, '_fin', FinancialIntegration(system=config.financial_system))
        object.__setattr__(self, '_bq', bq_service)

    @property
    def crm(self):
        return self._crm

    @property
    def erp(self):
        return self._erp

    @property
    def fin(self):
        return self._fin

    @property
    def bq(self):
        return self._bq

    def get_revenue_kpis(self) -> List[BusinessKPIData]:
        records = self.crm.fetch_metrics(['revenue'])
        self.bq.insert_rows('business_metrics', records)
        return [BusinessKPIData(**r) for r in records]

    def get_customer_kpis(self) -> List[BusinessKPIData]:
        records = self.crm.fetch_metrics(['customer'])
        self.bq.insert_rows('business_metrics', records)
        return [BusinessKPIData(**r) for r in records]

    def get_operational_kpis(self) -> List[BusinessKPIData]:
        records = self.erp.fetch_metrics(['operations'])
        self.bq.insert_rows('business_metrics', records)
        return [BusinessKPIData(**r) for r in records]

    def get_financials(self) -> List[BusinessKPIData]:
        data = self.fin.fetch_financials(['budget', 'savings'])
        # Convert to KPI records list format
        records = [
            {
                'metric_name': k,
                'metric_value': v,
                'metric_unit': 'USD',
                'timestamp': data['timestamp'],
                'business_unit': 'Finance',
                'ai_system_id': None,
                'metadata': {}
            }
            for k, v in data.items() if k in ['budget', 'savings']
        ]
        self.bq.insert_rows('business_metrics', records)
        return [BusinessKPIData(**r) for r in records]