# app/services/bigquery_service.py

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

from app.utils.config import PlatformConfig


class BigQueryService:
    """Service for managing BigQuery operations and data analysis."""
    
    def __init__(self, config: PlatformConfig):
        self.client = bigquery.Client(project=config.project_id)
        self.project_id = config.project_id
        self.dataset_id = config.bigquery_dataset
        self.dataset_ref = self.client.dataset(self.dataset_id)
        
        # Ensure dataset exists
        self._create_dataset_if_not_exists()
        self._create_tables_if_not_exist()
    
    def _create_dataset_if_not_exists(self):
        """Create BigQuery dataset if it doesn't exist."""
        try:
            self.client.get_dataset(self.dataset_ref)
        except NotFound:
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"
            dataset.description = "AI Infrastructure ROI Platform data"
            self.client.create_dataset(dataset)
    
    def _create_tables_if_not_exist(self):
        """Create required tables if they don't exist."""
        tables_schemas = {
            "infrastructure_metrics": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("project_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("service_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("resource_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("cost_usd", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("usage_amount", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("usage_unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("region", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
            ],
            "business_metrics": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metric_value", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("metric_unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("business_unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("ai_system_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
            ],
            "roi_correlations": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("ai_system_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("infrastructure_cost", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("business_value", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("roi_score", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("confidence_level", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("correlation_metadata", "JSON", mode="NULLABLE"),
            ],
            "rl_model_states": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("model_version", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("state_vector", "JSON", mode="NULLABLE"),
                bigquery.SchemaField("action_taken", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("reward_received", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("next_state_vector", "JSON", mode="NULLABLE"),
            ],
            "forecasts": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("metric_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("forecast_value", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("prediction_horizon", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("confidence_interval", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("insights", "STRING", mode="NULLABLE"),
            ],
            "benchmarks": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("benchmark_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("entity_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("baseline_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("performance_score", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("baseline_score", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("metric", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("score_unit", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("deviation", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("comment", "STRING", mode="NULLABLE"),
            ],
            "carbon_metrics": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("region", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("workload_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("cloud_provider", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("estimated_kg_co2e", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("emission_intensity", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("renewable_percent", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("greener_alternative_region", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("potential_saving_kg_co2e", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("recommendation", "STRING", mode="NULLABLE"),
            ],
            "compliance_findings": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("check_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("resource", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("severity", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("description", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("remediation", "STRING", mode="NULLABLE"),
            ],
            "vendor_risks": [
                bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("service_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("cloud_provider", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("current_dependency_score", "FLOAT64", mode="REQUIRED"),
                bigquery.SchemaField("estimated_exit_cost_usd", "FLOAT64", mode="NULLABLE"),
                bigquery.SchemaField("multi_cloud_feasibility", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("recommendation", "STRING", mode="NULLABLE"),
            ],
        }

        for table_name, schema in tables_schemas.items():
            table_ref = self.dataset_ref.table(table_name)
            try:
                self.client.get_table(table_ref)
            except NotFound:
                table = bigquery.Table(table_ref, schema=schema)
                self.client.create_table(table)

    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]):
        """Insert multiple rows into a BigQuery table."""
        table_ref = self.dataset_ref.table(table_name)
        errors = self.client.insert_rows_json(table_ref, rows)
        if errors:
            raise RuntimeError(f"Failed to insert rows into {table_name}: {errors}")

    def fetch_business_metrics(
        self, date_range: str = "30d", metrics_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch business metrics from BigQuery for analysis."""
        # Extract number and unit
        import re
        match = re.match(r"(\d+)([a-zA-Z]+)", date_range)
        if not match:
            raise ValueError("Invalid date_range format. Use like '30d' or '2w'")
        num, unit = match.groups()
        unit = unit.upper()
        if unit == "D":
            unit = "DAY"
        elif unit == "W":
            unit = "WEEK"
        elif unit == "M":
            unit = "MONTH"
        else:
            raise ValueError(f"Unsupported interval unit: {unit}")
        
        query = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.business_metrics` "
        query += f"WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {num} {unit})"
        if metrics_filter:
            filters = ",".join([f"'{m}'" for m in metrics_filter])
            query += f" AND metric_name IN ({filters})"
        df = self.client.query(query).to_dataframe()
        return df.to_dict(orient="records")


    def correlate_business_ai_metrics(
        self, business_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform correlation analysis between business and AI infra metrics."""
        # For simplicity, join with infra_metrics on timestamps
        infra_query = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.infrastructure_metrics`"
        infra_df = self.client.query(infra_query).to_dataframe()
        biz_df = pd.DataFrame(business_data)
        merged = pd.merge(biz_df, infra_df, on="timestamp", how="inner")

        # Example: linear regression per metric
        correlations = []
        for metric in biz_df['metric_name'].unique():
            sub = merged[merged['metric_name'] == metric]
            if len(sub) < 5: continue
            X = sub[['cost_usd']].values
            y = sub['metric_value'].values
            model = LinearRegression().fit(X, y)
            preds = model.predict(X)
            mse = mean_squared_error(y, preds)
            correlations.append({
                "metric": metric,
                "coeff": model.coef_[0].item(),
                "intercept": model.intercept_.item(),
                "mse": mse,
            })
        return correlations

    def calculate_ai_roi(
        self,
        business_data: List[Dict[str, Any]],
        correlation_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Calculate ROI scores for AI systems based on correlation analysis."""
        roi_scores = []
        for c in correlation_data:
            roi = c['coeff'] / (abs(c['mse']) + 1)
            roi_scores.append({
                "metric": c['metric'],
                "roi_score": roi,
            })
        return roi_scores

    def analyze_metric_trends(
        self, business_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze trends in business metrics over time."""
        biz_df = pd.DataFrame(business_data)
        trends = {}
        for metric in biz_df['metric_name'].unique():
            sub = biz_df[biz_df['metric_name'] == metric].copy()
            sub['timestamp'] = pd.to_datetime(sub['timestamp'])
            sub.set_index('timestamp', inplace=True)
            resampled = sub['metric_value'].resample('D').mean().fillna(method='ffill')
            trend = resampled.pct_change().mean()
            trends[metric] = trend.item()
        return trends

    def get_historical_infrastructure_data(self) -> List[Dict[str, Any]]:
        """Retrieve historical infra metrics for forecasting."""
        query = f"SELECT * FROM `{self.project_id}.{self.dataset_id}.infrastructure_metrics`"
        df = self.client.query(query).to_dataframe()
        return df.to_dict(orient="records")

    def calculate_comprehensive_roi(self) -> Dict[str, Any]:
        """Aggregate ROI across all metrics and systems."""
        biz_query = f"SELECT SUM(metric_value) as total_value FROM `{self.project_id}.{self.dataset_id}.business_metrics`"
        cost_query = f"SELECT SUM(cost_usd) as total_cost FROM `{self.project_id}.{self.dataset_id}.infrastructure_metrics`"
        total_value = self.client.query(biz_query).to_dataframe().iloc[0]['total_value']
        total_cost = self.client.query(cost_query).to_dataframe().iloc[0]['total_cost']
        overall_roi = (total_value - total_cost) / total_cost if total_cost else None
        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "overall_roi": overall_roi,
        }

    # Additional BigQueryService methods (e.g., calculate_custom_kpis) can be added here
    def calculate_custom_kpis(self, kpi_names: List[str]) -> List[Dict[str, Any]]:
        """Calculate and return values for custom KPIs specified by name."""
        placeholders = ','.join(f"'{k}'" for k in kpi_names)
        query = (
            f"SELECT metric_name, SUM(metric_value) as metric_value "
            f"FROM `{self.project_id}.{self.dataset_id}.business_metrics` "
            f"WHERE metric_name IN ({placeholders}) "
            f"GROUP BY metric_name"
        )
        df = self.client.query(query).to_dataframe()
        return df.to_dict(orient="records")