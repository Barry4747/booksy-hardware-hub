import pytest
from unittest.mock import patch, MagicMock
from app.services.audit import AuditService
from app.repositories.hardware import HardwareRepository
from app.schemas.audit import AuditReport, AuditIssue, SeverityEnum

def test_gemini_audit_success(db_session):
    hw_repo = HardwareRepository(db_session)
    service = AuditService(db_session, hw_repo)
    
    mock_response = MagicMock()
    mock_response.text = """
    ```json
    {
      "issues": [
        {
          "hardware_id": 1,
          "hardware_name": "Test Laptop",
          "severity": "critical",
          "issue": "Missing purchase date",
          "recommendation": "Update records"
        }
      ],
      "summary": "Found 1 critical issue."
    }
    ```
    """
    
    with patch.object(service.model, 'generate_content', return_value=mock_response) as mock_gen:
        report = service.run_audit()
        
        mock_gen.assert_called_once()
        assert isinstance(report, AuditReport)
        assert len(report.issues) == 1
        assert report.issues[0].hardware_id == 1
        assert report.issues[0].hardware_name == "Test Laptop"
        assert report.issues[0].severity == SeverityEnum.CRITICAL
        assert report.summary == "Found 1 critical issue."

def test_gemini_audit_parse_failure(db_session):
    hw_repo = HardwareRepository(db_session)
    service = AuditService(db_session, hw_repo)
    
    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON at all!"
    
    with patch.object(service.model, 'generate_content', return_value=mock_response):
        report = service.run_audit()
        
        assert isinstance(report, AuditReport)
        assert len(report.issues) == 0
        assert report.summary == "Audit failed to parse AI response"
