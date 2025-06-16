import datetime

def fetch_kpis_from_crm(category: str) -> dict:
    if category == "revenue":
        return {
            "mrr": 500000,
            "arr": 6000000,
            "ltv": 12000,
            "churn_rate": 0.05,
            "timestamp": datetime.datetime.now().isoformat()
        }
    elif category == "customer":
        return {
            "csat": 87.5,
            "nps": 43,
            "churn_rate": 0.04,
            "timestamp": datetime.datetime.now().isoformat()
        }
    return {}

def fetch_kpis_from_erp(category: str) -> dict:
    if category == "operations":
        return {
            "ops_cost": 320000,
            "timestamp": datetime.datetime.now().isoformat()
        }
    return {}
