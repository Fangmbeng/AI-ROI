from pydantic import BaseModel
from typing import Optional

class BusinessKPIData(BaseModel):
    mrr: Optional[float] = None
    arr: Optional[float] = None
    ltv: Optional[float] = None
    churn_rate: Optional[float] = None
    csat: Optional[float] = None
    nps: Optional[float] = None
    ops_cost: Optional[float] = None
    timestamp: Optional[str] = None
