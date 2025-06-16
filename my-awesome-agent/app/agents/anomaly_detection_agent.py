from vertexai.preview.reasoning_engines import LangchainAgent
from app.services.bigquery_service import BigQueryService
from app.services.monitoring_service import MonitoringService
from app.services.gcp_billing_service import GCPBillingService
from app.services.integration_service import CRMIntegration, ERPIntegration, FinancialIntegration
from app.utils.config import PlatformConfig
from app.tools.anomaly_tools import detect_anomalies
from app.models.anomaly import Anomaly
from google.adk.agents import LlmAgent


class AnomalyDetectionAgent(LlmAgent):
    def __init__(
        self,
        config: PlatformConfig,
        bq_service: BigQueryService,
        monitoring_service: MonitoringService,
        billing_service: GCPBillingService,
    ):
        # Call parent constructor first
        super().__init__(
            name="anomaly_detection_agent",
            model="gemini-2.0-flash",
            tools=[self.flag_anomalies],
            description="Detect and correlate anomalies across cost, usage, business KPIs, and financial data."
        )
        
        # Initialize services using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_config', config)
        object.__setattr__(self, '_bq', bq_service)
        object.__setattr__(self, '_monitoring', monitoring_service)
        object.__setattr__(self, '_billing', billing_service)
        object.__setattr__(self, '_crm', CRMIntegration(system=config.crm_system))
        object.__setattr__(self, '_erp', ERPIntegration(system=config.erp_system))
        object.__setattr__(self, '_fin', FinancialIntegration(system=config.financial_system))

    @property
    def config(self):
        return self._config

    @property
    def bq(self):
        return self._bq

    @property
    def monitoring(self):
        return self._monitoring

    @property
    def billing(self):
        return self._billing

    @property
    def crm(self):
        return self._crm

    @property
    def erp(self):
        return self._erp

    @property
    def fin(self):
        return self._fin

    def flag_anomalies(self) -> list[Anomaly]:
        return detect_anomalies(
            config=self.config,
            bq=self.bq,
            monitoring=self.monitoring,
            billing=self.billing,
            crm=self.crm,
            erp=self.erp,
            fin=self.fin,
        )