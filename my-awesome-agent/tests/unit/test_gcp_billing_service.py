# tests/unit/test_gcp_billing_service.py

import pytest
from app.services.gcp_billing_service import GCPBillingService
from app.utils.config import PlatformConfig

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-proj")
    return PlatformConfig.from_env()

def test_aggregate_by_service(set_env):
    service = GCPBillingService(set_env)
    data = [
        {"service": "A", "cost": 10},
        {"service": "B", "cost": 20},
        {"service": "A", "cost": 5},
    ]
    agg = service.aggregate_by_service(data)
    assert agg == {"A": 15, "B": 20}

def test_identify_cost_savings(set_env):
    service = GCPBillingService(set_env)
    data = [
        {"service": "X", "cost": 35000},
        {"service": "Y", "cost": 10000},
    ]
    savings = service.identify_cost_savings(data)
    assert "X" in savings
    assert "Review committed use discounts" in savings["X"][0]

def test_get_gpu_utilization_metrics(set_env):
    service = GCPBillingService(set_env)
    gpu = service.get_gpu_utilization_metrics("test-proj")
    assert "gpu_utilization_pct" in gpu
    assert isinstance(gpu["gpu_utilization_pct"], float)
