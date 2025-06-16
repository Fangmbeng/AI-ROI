from pydantic import BaseModel

class Anomaly(BaseModel):
    type: str  # "Cost Spike", "KPI Drop", "Model Drift", etc.
    timestamp: str
    affected_component: str  # Model ID, service, or dataset
    severity: str  # "Critical", "Moderate", "Low"
    description: str
    suggested_action: str
