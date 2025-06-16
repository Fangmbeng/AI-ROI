from pydantic import BaseModel

class BenchmarkResult(BaseModel):
    benchmark_type: str  # "Model", "Cost", "Infra"
    entity_name: str  # e.g., "Churn Model v2", "us-central1"
    baseline_name: str  # e.g., "Industry Avg", "Internal Q1 Target"
    performance_score: float
    baseline_score: float
    metric: str
    score_unit: str
    deviation: float  # % difference
    comment: str
