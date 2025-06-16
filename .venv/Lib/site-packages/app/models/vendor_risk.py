# app/models/vendor_risk.py

from pydantic import BaseModel

class VendorLockinRisk(BaseModel):
    service_name: str           # e.g., "BigQuery", "Vertex AI Pipelines"
    cloud_provider: str         # e.g., "GCP", "AWS", "Azure"
    current_dependency_score: float  # 0–1, where 1 = fully locked in
    estimated_exit_cost_usd: float
    multi_cloud_feasibility: str     # e.g., "High", "Medium", "Low"
    recommendation: str              # suggested strategy
    analysis_timestamp: str
