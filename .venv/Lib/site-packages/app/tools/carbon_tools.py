from app.models.carbon import CarbonFootprint

def estimate_carbon_footprint() -> list[CarbonFootprint]:
    return [
        CarbonFootprint(
            region="us-west1",
            workload_name="Vertex AI GPT Inference",
            cloud_provider="Google Cloud",
            estimated_kg_co2e=125.4,
            emission_intensity=393.0,
            renewable_percent=43.0,
            greener_alternative_region="finland-north",
            potential_saving_kg_co2e=72.5,
            recommendation="Migrate to finland-north (90% renewables) for lower carbon footprint"
        ),
        CarbonFootprint(
            region="us-east1",
            workload_name="BigQuery Analytics Batch",
            cloud_provider="Google Cloud",
            estimated_kg_co2e=48.1,
            emission_intensity=450.2,
            renewable_percent=38.5,
            greener_alternative_region="canada-central",
            potential_saving_kg_co2e=31.2,
            recommendation="Move to canada-central to reduce emissions by ~65%"
        )
    ]
