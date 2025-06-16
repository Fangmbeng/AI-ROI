# app/agents/performance_correlation_agent.py
import json
from datetime import datetime
from typing import List
from vertexai.preview.reasoning_engines import ReasoningEngine, LangchainAgent
from app.models.performance_correlation import CorrelationInsight
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig
from google.adk.agents import LlmAgent


class PerformanceCorrelationAgent(LlmAgent):
    def __init__(self, config: PlatformConfig, bq_service: BigQueryService):

        super().__init__(
            name="performance_correlation_agent",
            model="gemini-2.0-flash",
            description="Correlates infra cost with business metrics and persists insights",
            tools=[self.get_correlation_insights],
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

    def get_correlation_insights(self) -> List[CorrelationInsight]:
        # 1) Fetch raw business and infra data
        business_data = self.bq.fetch_business_metrics()
        infra_data = self.bq.get_historical_infrastructure_data()
        # 2) Perform correlation
        correlation_results = self.bq.correlate_business_ai_metrics(business_data)
        # 3) Calculate ROI
        roi_scores = self.bq.calculate_ai_roi(business_data, correlation_results)
        # 4) Combine into insights and persist
        insights = []
        timestamp = datetime.utcnow().isoformat()
        rows = []
        for corr, roi in zip(correlation_results, roi_scores):
            insight = CorrelationInsight(
                workload=corr["metric"],
                model_id="N/A",
                cost=corr["coeff"],              # placeholder
                kpi_impact_score=corr["coeff"],
                roi_score=roi["roi_score"],
                comment=f"Coeff={corr['coeff']:.2f}, MSE={corr['mse']:.2f}"  # Fixed: removed \", added missing comma
            )
            insights.append(insight)
            rows.append({
                "timestamp": timestamp,
                "ai_system_id": corr["metric"],
                "infrastructure_cost": corr["coeff"],
                "business_value": corr["coeff"] * corr["coeff"],
                "roi_score": insight.roi_score,
                "confidence_level": 1.0,
                "correlation_metadata": json.dumps(corr),
            })
        # Persist to BigQuery
        self.bq.insert_rows("roi_correlations", rows)
        return insights
