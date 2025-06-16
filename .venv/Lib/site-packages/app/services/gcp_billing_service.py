from datetime import datetime
from typing import List, Dict, Optional

from google.cloud.monitoring_v3 import MetricServiceClient
from google.cloud.billing_v1 import CloudBillingClient

from app.utils.config import PlatformConfig


class GCPBillingService:
    """Service for retrieving and analyzing GCP billing and usage data."""

    def __init__(self, config: PlatformConfig):
        self.project_id = config.project_id
        self.billing_client = CloudBillingClient()
        self.metric_client = MetricServiceClient()

    def get_detailed_billing_data(
        self, project_id: str, start_date: str, end_date: str, service_filter: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """Fetch detailed billing data from GCP between dates, optionally filtered by service."""
        # Build BigQuery export query or use Billing API if available
        # Placeholder: return mocked data list
        return [
            {"service": "Compute Engine", "cost": 50000, "usage": 1200, "unit": "vCPU-hours", "date": start_date},
            {"service": "BigQuery", "cost": 20000, "usage": 300, "unit": "TB-processed", "date": end_date},
        ]

    def aggregate_by_service(self, cost_data: List[Dict[str, any]]) -> Dict[str, float]:
        """Aggregate total cost per GCP service."""
        agg: Dict[str, float] = {}
        for item in cost_data:
            svc = item.get("service")
            cost = item.get("cost", 0.0)
            agg[svc] = agg.get(svc, 0.0) + cost
        return agg

    def analyze_usage_patterns(self, cost_data: List[Dict[str, any]]) -> Dict[str, Dict[str, float]]:
        """Analyze usage patterns, returning stats per service."""
        patterns: Dict[str, List[float]] = {}
        for item in cost_data:
            svc = item.get("service")
            usage = item.get("usage", 0.0)
            patterns.setdefault(svc, []).append(usage)
        return {svc: {"avg_usage": sum(vals)/len(vals), "max_usage": max(vals)} for svc, vals in patterns.items()}

    def identify_cost_savings(self, cost_data: List[Dict[str, any]]) -> Dict[str, List[str]]:
        """Identify quick-win cost savings opportunities."""
        savings: Dict[str, List[str]] = {}
        for item in cost_data:
            svc = item.get("service")
            if item.get("cost", 0) > 30000:
                savings.setdefault(svc, []).append("Review committed use discounts and rightsizing opportunities.")
        return savings

    def get_gpu_utilization_metrics(self, project_id: str) -> Dict[str, float]:
        """Retrieve GPU utilization metrics for the project."""
        # Placeholder logic for GPU utilization
        return {"gpu_utilization_pct": 78.5, "average_gpu_hours": 120.0}

    def get_current_infrastructure_state(self) -> Dict[str, any]:
        """Get snapshot of current infra state including services, quotas, and usage."""
        # Placeholder: return basic state
        return {
            "project_id": self.project_id,
            "services": ["Compute Engine", "BigQuery", "Vertex AI"],
            "quotas": {"vCPU": 200, "TPU": 10},
            "usage": {"vCPU": 150, "TPU": 5},
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_executive_cost_summary(self, report_type: str) -> Dict[str, any]:
        """Return aggregated cost summary for executive reports."""
        # Placeholder summarization
        return {"total_cost": 320000.0, "by_service": self.aggregate_by_service(self.get_detailed_billing_data(self.project_id, "2025-05-01", "2025-05-31"))}

    def get_recent_usage_data(self, lookback_period: str) -> List[Dict[str, any]]:
        """Fetch recent usage data for anomaly detection, based on lookback period."""
        # Placeholder: return same as detailed data
        return self.get_detailed_billing_data(self.project_id, "2025-06-06", "2025-06-13")