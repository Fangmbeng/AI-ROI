from datetime import datetime
from typing import List
from app.models.anomaly import Anomaly
from app.services.monitoring_service import MonitoringService
from app.services.gcp_billing_service import GCPBillingService
from app.services.vertex_ai_service import VertexAIService
from app.services.integration_service import CRMIntegration, ERPIntegration, FinancialIntegration
from app.services.bigquery_service import BigQueryService
from app.utils.config import PlatformConfig


def detect_anomalies(
    config: PlatformConfig,
    bq: BigQueryService,
    billing: GCPBillingService,
    vertex: VertexAIService,
    monitoring: MonitoringService,
    crm: CRMIntegration,
    erp: ERPIntegration,
    fin: FinancialIntegration,
) -> List[Anomaly]:
    """
    Detect anomalies across infrastructure and business metrics.
    """
    now = datetime.utcnow()
    lookback = "7d"
    anomalies: List[Anomaly] = []

    # 1. Cost Anomalies
    cost_data = billing.get_recent_usage_data(lookback)
    anomalies.extend([
        Anomaly(
            type="Cost Spike",
            timestamp=now.isoformat(),
            affected_component=item.get("service"),
            severity="Critical" if item.get("cost", 0) > 50000 else "Moderate",
            description=f"{item.get('service')} cost changed by {item.get('cost')} USD",
            suggested_action="Review billing details and scaling policies"
        )
        for item in cost_data if item.get("cost", 0) > 40000
    ])

    # 2. CPU Anomalies
    cpu_metrics = monitoring.get_recent_cpu_utilization(60)
    anomalies.extend([
        Anomaly(
            type="CPU Spike",
            timestamp=pt["timestamp"],
            affected_component="Compute Engine Instance",
            severity="High" if pt["value"] > 0.85 else "Low",
            description=f"CPU utilization at {pt['value']:.2f}",
            suggested_action="Scale down or optimize workloads"
        ) for pt in cpu_metrics if pt.get("value", 0) > 0.90
    ])

    # 3. Memory Anomalies
    mem_metrics = monitoring.get_memory_utilization(60)
    anomalies.extend([
        Anomaly(
            type="Memory Spike",
            timestamp=pt["timestamp"],
            affected_component="Compute Engine Instance",
            severity="High" if pt["value"] > 0.85 else "Low",
            description=f"Memory utilization at {pt['value']:.2f}",
            suggested_action="Investigate memory leaks or increase instance size"
        ) for pt in mem_metrics if pt.get("value", 0) > 0.90
    ])

    # 4. Disk I/O Anomalies
    disk_metrics = monitoring.get_disk_io(60)
    anomalies.extend([
        Anomaly(
            type="Disk I/O Anomaly",
            timestamp=pt["timestamp"],
            affected_component="Compute Engine Disk",
            severity="Moderate" if pt["value"] > 300 else "Low",
            description=f"Disk I/O time at {pt['value']:.2f} seconds",
            suggested_action="Check disk performance or scale disk throughput"
        ) for pt in disk_metrics if pt.get("value", 0) > 200
    ])

    # 5. Network Anomalies
    net_metrics = monitoring.get_network_traffic(60)
    anomalies.extend([
        Anomaly(
            type="Network Traffic Spike",
            timestamp=pt["timestamp"],
            affected_component="Compute Engine Network",
            severity="High" if pt["value"] > 1e7 else "Low",
            description=f"Network received bytes: {pt['value']}",
            suggested_action="Validate expected workload patterns or check for data exfiltration"
        ) for pt in net_metrics if pt.get("value", 0) > 5e6
    ])

    # 6. CRM Anomalies (e.g., sharp drop in CSAT or lead conversions)
    crm_metrics = crm.fetch_metrics(["csat", "lead_conversion"])
    for metric in crm_metrics:
        if metric["metric_name"] == "csat" and metric["metric_value"] < 3.0:
            anomalies.append(Anomaly(
                type="Low CSAT",
                timestamp=metric["timestamp"],
                affected_component="CRM",
                severity="High",
                description=f"Customer satisfaction dropped to {metric['metric_value']}",
                suggested_action="Investigate customer feedback and complaints"
            ))
        if metric["metric_name"] == "lead_conversion" and metric["metric_value"] < 0.05:
            anomalies.append(Anomaly(
                type="Low Conversion Rate",
                timestamp=metric["timestamp"],
                affected_component="CRM",
                severity="Moderate",
                description=f"Lead conversion rate is only {metric['metric_value']*100:.1f}%",
                suggested_action="Audit sales funnel and lead qualification process"
            ))

    # 7. ERP Anomalies (e.g., supply delays or process duration spikes)
    erp_metrics = erp.fetch_metrics(["order_fulfillment_time", "inventory_turnover"])
    for metric in erp_metrics:
        if metric["metric_name"] == "order_fulfillment_time" and metric["metric_value"] > 7:
            anomalies.append(Anomaly(
                type="Fulfillment Delay",
                timestamp=metric["timestamp"],
                affected_component="ERP",
                severity="High",
                description=f"Order fulfillment time is {metric['metric_value']} days",
                suggested_action="Check supply chain bottlenecks"
            ))

    # 8. Financial Anomalies (e.g., budget overspending or missed savings)
    fin_data = fin.fetch_financials(["budget", "savings"])
    if fin_data.get("budget", 0) > 1000000:
        anomalies.append(Anomaly(
            type="Budget Overrun",
            timestamp=fin_data["timestamp"],
            affected_component="Finance",
            severity="Critical",
            description=f"Budget consumption exceeded $1M",
            suggested_action="Review expenditure and reallocate resources"
        ))

    if fin_data.get("savings", 0) < 10000:
        anomalies.append(Anomaly(
            type="Low Savings",
            timestamp=fin_data["timestamp"],
            affected_component="Finance",
            severity="Moderate",
            description=f"Savings dropped below $10k",
            suggested_action="Investigate cost-saving strategies"
        ))

    return anomalies
