import pytest
from app.services.audit import AuditService
from app.repositories.hardware import HardwareRepository
from app.models.hardware import HardwareStatus

def test_run_audit(db_session):
    hw_repo = HardwareRepository(db_session)
    service = AuditService(db_session, hw_repo)
    
    # Create test data
    hw_repo.create(name="XPS", brand="Dell", status=HardwareStatus.REPAIR) # Should be flagged
    hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE, purchase_date=None) # Should be flagged
    hw_repo.create(name="ThinkPad", brand="Lenovo", status=HardwareStatus.IN_USE) # Wait, it has no purchase date so it should be flagged too
    db_session.commit()
    
    report = service.run_audit()
    
    assert report.summary.startswith("Audit completed")
    assert len(report.issues) == 4 # 1 for repair, 3 for missing purchase dates (since none of them have purchase_date provided)
    
    repair_issues = [i for i in report.issues if i.name.startswith("Device in repair")]
    assert len(repair_issues) == 1
    
    missing_date_issues = [i for i in report.issues if i.name.startswith("Missing purchase date")]
    assert len(missing_date_issues) == 3
