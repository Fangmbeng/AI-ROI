from pydantic import BaseModel

class Forecast(BaseModel):
    category: str  # "Cost", "KPI", "Usage"
    metric_name: str
    forecast_value: float
    unit: str
    prediction_horizon: str  # e.g., "7 days", "1 month"
    confidence_interval: str  # e.g., "95%"
    insights: str  # Optional comment for interpretation
