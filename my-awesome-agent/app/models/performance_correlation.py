from pydantic import BaseModel

class CorrelationInsight(BaseModel):
    workload: str
    model_id: str
    cost: float
    kpi_impact_score: float  # Value from -1 to 1
    roi_score: float         # Normalized ROI score, e.g., from -100 to 100
    comment: str
