from sqlalchemy.orm import Session
from app.repositories.hardware import HardwareRepository
from app.schemas.audit import AuditReport, AuditIssue, SeverityEnum
import uuid

class AuditService:
    def __init__(self, db: Session, hw_repo: HardwareRepository):
        self.db = db
        self.hw_repo = hw_repo

    def run_audit(self) -> AuditReport:
        hardware_list = self.hw_repo.list(limit=1000)
        issues = []
        
        # MOCK LOGIC: AI Simulation
        for hw in hardware_list:
            if hw.status.value == "Repair":
                issues.append(
                    AuditIssue(
                        id=str(uuid.uuid4()),
                        name=f"Device in repair: {hw.name}",
                        severity=SeverityEnum.WARNING,
                        issue=f"Device {hw.brand} {hw.name} (ID: {hw.id}) has been marked for repair.",
                        recommendation="Check the repair logs and estimate return time."
                    )
                )
            
            # Additional dummy check
            if not hw.purchase_date:
                issues.append(
                    AuditIssue(
                        id=str(uuid.uuid4()),
                        name=f"Missing purchase date: {hw.name}",
                        severity=SeverityEnum.INFO,
                        issue=f"Device {hw.name} (ID: {hw.id}) is missing a purchase date.",
                        recommendation="Update inventory with accurate purchase dates to track warranty."
                    )
                )

        return AuditReport(
            issues=issues,
            summary=f"Audit completed. Found {len(issues)} potential issues across {len(hardware_list)} hardware items."
        )
