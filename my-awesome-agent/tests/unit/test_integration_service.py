# tests/unit/test_integration_service.py

import pytest
from app.services.integration_service import CRMIntegration, ERPIntegration, FinancialIntegration


def test_crm_integration_revenue():
    crm = CRMIntegration(system='Salesforce')
    records = crm.fetch_metrics(['revenue'])
    assert isinstance(records, list)
    assert records, "Expected at least one revenue record"
    rec = records[0]
    assert rec.get('metric_name') == 'ARR'
    assert isinstance(rec.get('metric_value'), float)
    assert rec.get('metric_unit') == 'USD'
    assert 'timestamp' in rec


def test_crm_integration_customer():
    crm = CRMIntegration(system='Salesforce')
    records = crm.fetch_metrics(['customer'])
    assert records, "Expected at least one customer record"
    rec = records[0]
    assert rec.get('metric_name') == 'CSAT'
    assert isinstance(rec.get('metric_value'), float)
    assert rec.get('metric_unit') == '%'


def test_erp_integration_operations():
    erp = ERPIntegration(system='SAP')
    records = erp.fetch_metrics(['operations'])
    assert records, "Expected at least one operations record"
    rec = records[0]
    assert rec.get('metric_name') == 'OpsCost'
    assert isinstance(rec.get('metric_value'), float)
    assert rec.get('metric_unit') == 'USD'


def test_financial_integration_budget_and_savings():
    fin = FinancialIntegration(system='QuickBooks')
    data = fin.fetch_financials(['budget', 'savings'])
    assert isinstance(data, dict)
    assert 'budget' in data and 'savings' in data
    assert isinstance(data['budget'], float)
    assert isinstance(data['savings'], float)
    assert 'timestamp' in data
