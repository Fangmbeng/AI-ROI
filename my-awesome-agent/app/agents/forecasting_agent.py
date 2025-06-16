# app/agents/forecasting_agent.py

from typing import List
from datetime import datetime
from vertexai.preview.reasoning_engines import ReasoningEngine, LangchainAgent
from google.adk.agents import LlmAgent

from app.models.forecast import Forecast
from app.services.bigquery_service import BigQueryService
from app.services.vertex_ai_service import VertexAIService
from app.utils.config import PlatformConfig

class ForecastingAgent(LlmAgent):
    def __init__(
        self,
        config: PlatformConfig,
        bq_service: BigQueryService,
        vertex_service: VertexAIService
    ):
        # Call parent constructor first
        super().__init__(
            name="forecasting_agent",
            model="gemini-2.0-flash",
            description="Predicts trends in cost, KPI and usage, persists forecasts",
            tools=[self.predict_ai_infra_trends],
        )
        
        # Initialize services using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, '_bq', bq_service)
        object.__setattr__(self, '_vertex', vertex_service)
        object.__setattr__(self, '_config', config)

    @property
    def bq(self):
        return self._bq

    @property
    def vertex(self):
        return self._vertex

    @property
    def config(self):
        return self._config

    def predict_ai_infra_trends(self) -> List[Forecast]:
        # 1) Fetch historical infra & business data
        infra_data = self.bq.get_historical_infrastructure_data()
        biz_data = self.bq.fetch_business_metrics()

        # 2) Call Vertex AI for forecasts
        horizon = "30d"
        forecasts = self.vertex.forecast_infrastructure_needs(infra_data, horizon)

        # 3) Transform into Forecast models and persist
        results: List[Forecast] = []
        rows = []
        ts = datetime.utcnow().isoformat()
        for f in forecasts:
            fc = Forecast(**{
                "category": "Cost" if "CPU" in f["resource"] else "Usage",
                "metric_name": f["resource"],
                "forecast_value": f["forecast"],
                "unit": f["unit"],
                "prediction_horizon": horizon,
                "confidence_interval": "90%",
                "insights": ""
            })
            results.append(fc)
            rows.append({
                "timestamp": ts,
                "category": fc.category,
                "metric_name": fc.metric_name,
                "forecast_value": fc.forecast_value,
                "unit": fc.unit,
                "prediction_horizon": fc.prediction_horizon,
                "confidence_interval": fc.confidence_interval,
                "insights": fc.insights,
            })
        self.bq.insert_rows("forecasts", rows)
        return results