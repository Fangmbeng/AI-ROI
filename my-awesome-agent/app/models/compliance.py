# app/models/compliance.py

from pydantic import BaseModel

class ComplianceFinding(BaseModel):
    check_name: str            # e.g. "IAM Least Privilege", "Data Encryption at Rest"
    resource: str              # resource identifier (e.g. "projects/my-proj/instances/…")
    status: str                # "PASS", "WARN", "FAIL"
    severity: str              # "Critical", "High", "Medium", "Low"
    description: str           # human-readable explanation
    remediation: str           # recommended fix or link to runbook
    timestamp: str             # when the check was performed
