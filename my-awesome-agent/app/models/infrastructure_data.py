from pydantic import BaseModel
from typing import Optional

class InfrastructureCostData(BaseModel):
    provider: str
    compute_cost: Optional[float] = None
    storage_cost: Optional[float] = None
    network_cost: Optional[float] = None
    total_cost: Optional[float] = None
    timestamp: Optional[str] = None
