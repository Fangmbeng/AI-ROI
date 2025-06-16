from pydantic import BaseModel

class CarbonFootprint(BaseModel):
    region: str
    workload_name: str
    cloud_provider: str
    estimated_kg_co2e: float
    emission_intensity: float  # gCO2e/kWh
    renewable_percent: float
    greener_alternative_region: str
    potential_saving_kg_co2e: float
    recommendation: str
