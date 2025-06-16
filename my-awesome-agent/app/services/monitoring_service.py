# app/services/monitoring_service.py

from typing import List, Dict, Any
from datetime import datetime, timedelta

from google.cloud import monitoring_v3
from google.api import metric_pb2
from google.api import service_pb2
from google.cloud.monitoring_v3 import MetricServiceClient, QueryTimeSeriesRequest, NotificationChannelServiceClient

from app.utils.config import PlatformConfig


class MonitoringService:
    """Service for retrieving and analyzing metrics from Cloud Monitoring."""

    def __init__(self, config: PlatformConfig):
        self.project_id = config.project_id
        self.client = MetricServiceClient()
        self.notification_client = NotificationChannelServiceClient()
        self.project_name = f"projects/{self.project_id}"

    def query_metric(
        self,
        metric_type: str,
        start_time: datetime,
        end_time: datetime,
        aggregation: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Query time series data for a given metric type."""
        interval = monitoring_v3.TimeInterval(
            {
                "start_time": start_time,
                "end_time": end_time,
            }
        )
        aggregation_proto = None
        if aggregation:
            aggregation_proto = monitoring_v3.Aggregation(**aggregation)

        request = QueryTimeSeriesRequest(
            name=self.project_name,
            query=f"fetch {metric_type}"
        )
        results = self.client.query_time_series(request=request)
        output = []
        for ts in results:
            for point in ts.points:
                output.append({
                    "metric": ts.metric.type,
                    "timestamp": point.interval.end_time.isoformat(),
                    "value": point.value.double_value if point.value.double_value else point.value.int64_value,
                })
        return output

    def list_notification_channels(self) -> List[Dict[str, Any]]:
        """List all notification channels configured in Cloud Monitoring."""
        channels = self.notification_client.list_notification_channels(
            name=self.project_name
        )
        return [
            {
                "name": ch.name,
                "type": ch.type_,
                "display_name": ch.display_name,
                "enabled": ch.enabled,
            }
            for ch in channels
        ]

    def create_alert_policy(
        self,
        display_name: str,
        metric_type: str,
        threshold_value: float,
        duration: timedelta,
        notification_channel_ids: List[str]
    ) -> Dict[str, Any]:
        """Create an alert policy for a specific metric threshold."""
        policy = monitoring_v3.AlertPolicy(
            display_name=display_name,
            combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.AND,
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name=f"{metric_type} threshold",
                    condition_monitoring_query_language=
                    monitoring_v3.AlertPolicy.Condition.MonitoringQueryLanguageCondition(
                        query=f"fetch {metric_type} | condition val() > {threshold_value}"
                    ),
                    duration=duration,
                )
            ],
            notification_channels=notification_channel_ids,
        )
        client = monitoring_v3.AlertPolicyServiceClient()
        created = client.create_alert_policy(
            name=self.project_name,
            alert_policy=policy
        )
        return {"name": created.name, "display_name": created.display_name}

    def get_recent_cpu_utilization(self, lookback_minutes: int = 60) -> List[Dict[str, Any]]:
        """Fetch recent CPU utilization metrics for all Compute Engine instances."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        return self.query_metric(
            metric_type="compute.googleapis.com/instance/cpu/utilization",
            start_time=start_time,
            end_time=end_time,
            aggregation={"alignment_period": {"seconds": 300}, "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MEAN}
        )

    def get_memory_utilization(self, lookback_minutes: int = 60) -> List[Dict[str, Any]]:
        """Fetch recent memory utilization metrics for all Compute Engine instances."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        return self.query_metric(
            metric_type="compute.googleapis.com/instance/memory/usage",
            start_time=start_time,
            end_time=end_time,
            aggregation={"alignment_period": {"seconds": 300}, "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MEAN}
        )

    def get_disk_io(self, lookback_minutes: int = 60) -> List[Dict[str, Any]]:
        """Fetch recent disk I/O metrics for all Compute Engine instances."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        return self.query_metric(
            metric_type="compute.googleapis.com/instance/disk/io_time",
            start_time=start_time,
            end_time=end_time,
            aggregation={"alignment_period": {"seconds": 300}, "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MAX}
        )

    def get_network_traffic(self, lookback_minutes: int = 60) -> List[Dict[str, Any]]:
        """Fetch recent network traffic metrics for all Compute Engine instances."""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=lookback_minutes)
        return self.query_metric(
            metric_type="compute.googleapis.com/instance/network/received_bytes_count",
            start_time=start_time,
            end_time=end_time,
            aggregation={"alignment_period": {"seconds": 300}, "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_SUM}
        )

    # Additional MonitoringService methods can be added here
