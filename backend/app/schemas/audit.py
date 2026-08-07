from pydantic import BaseModel
from enum import Enum
from typing import List

class SeverityEnum(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class AuditIssue(BaseModel):
    hardware_id: int
    hardware_name: str
    severity: SeverityEnum
    issue: str
    recommendation: str

class AuditReport(BaseModel):
    issues: List[AuditIssue]
    summary: str
