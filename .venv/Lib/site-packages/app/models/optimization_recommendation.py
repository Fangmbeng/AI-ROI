from pydantic import BaseModel

class OptimizationRecommendation(BaseModel):
    workload: str
    model_id: str
    action: str  # e.g., "Scale Up", "Scale Down", "Replace Model", "Decommission"
    expected_impact: str
    rationale: str
