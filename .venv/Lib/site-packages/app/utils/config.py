# app/utils/config.py

import os
from dataclasses import dataclass
from typing import Dict

@dataclass
class AgentConfig:
    name: str
    model: str
    max_iterations: int
    timeout_seconds: int
    tools: list[str]

@dataclass
class PlatformConfig:
    project_id: str
    location: str
    bigquery_dataset: str
    vertex_ai_location: str
    crm_system: str
    erp_system: str
    financial_system: str
    agents: Dict[str, AgentConfig]

    @classmethod
    def from_env(cls):
        project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        dataset = os.getenv("BIGQUERY_DATASET", "ai_roi_platform")
        vertex_loc = os.getenv("VERTEX_AI_LOCATION", location)
        crm = os.getenv("CRM_SYSTEM", "Salesforce")
        erp = os.getenv("ERP_SYSTEM", "SAP")
        fin = os.getenv("FINANCIAL_SYSTEM", "QuickBooks")
        # Agents config can be loaded from YAML later
        agents = {}
        return cls(
            project_id=project,
            location=location,
            bigquery_dataset=dataset,
            vertex_ai_location=vertex_loc,
            crm_system=crm,
            erp_system=erp,
            financial_system=fin,
            agents=agents,
        )
