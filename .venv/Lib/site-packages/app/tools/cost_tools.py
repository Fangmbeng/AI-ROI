import datetime

def fetch_cloud_costs(provider: str) -> dict:
    timestamp = datetime.datetime.now().isoformat()
    if provider == "GCP":
        return {
            "compute_cost": 75000,
            "storage_cost": 21000,
            "network_cost": 9000,
            "total_cost": 105000,
            "timestamp": timestamp
        }
    elif provider == "AWS":
        return {
            "compute_cost": 85000,
            "storage_cost": 29000,
            "network_cost": 11000,
            "total_cost": 125000,
            "timestamp": timestamp
        }
    return {
        "compute_cost": 0,
        "storage_cost": 0,
        "network_cost": 0,
        "total_cost": 0,
        "timestamp": timestamp
    }
