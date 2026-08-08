import json
from google import genai
from sqlalchemy.orm import Session
from app.repositories.hardware import HardwareRepository
from app.schemas.audit import AuditReport, AuditIssue, SeverityEnum
from app.core.config import settings
from app.exceptions.audit import AuditGenerationError

from fastapi.concurrency import run_in_threadpool

class AuditService:
    def __init__(self, db: Session, hw_repo: HardwareRepository):
        self.db = db
        self.hw_repo = hw_repo
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def run_audit(self) -> AuditReport:
        hardware_list = self.hw_repo.list(limit=1000)
        
        hw_dicts = []
        for hw in hardware_list:
            hw_dicts.append({
                "id": hw.id,
                "name": hw.name,
                "brand": hw.brand,
                "purchase_date": hw.purchase_date.isoformat() if hw.purchase_date else None,
                "status": hw.status.value if hasattr(hw.status, 'value') else str(hw.status),
                "notes": hw.notes,
                "has_active_rental": any(r.returned_at is None for r in hw.rentals) if hw.rentals else False
            })

        inventory_json = json.dumps(hw_dicts, indent=2)

        prompt = f"""You are an inventory auditor for a hardware management system.
Analyze the following hardware inventory and identify anomalies.

Return ONLY valid JSON in this exact format, no markdown, no explanation:
{{
  "issues": [
    {{
      "hardware_id": <int>,
      "hardware_name": "<str>",
      "severity": "<critical|warning|info>",
      "issue": "<short description>",
      "recommendation": "<what to do>"
    }}
  ],
  "summary": "<one sentence overall assessment>"
}}

Flag these issues:
- Purchase dates in the future
- Missing or empty brand names
- Possible brand name typos
- Items with damage mentioned in notes but status Available
- Items with status In Use but no active rental record
- Any other inconsistencies that would concern an IT manager

Inventory:
{inventory_json}"""

        def call_gemini():
            return self.client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )

        try:
            response = await run_in_threadpool(call_gemini)
            
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            
            raw_text = raw_text.strip()
            
            data = json.loads(raw_text)
            
            issues = []
            for item in data.get("issues", []):
                issues.append(
                    AuditIssue(
                        hardware_id=item.get("hardware_id"),
                        hardware_name=item.get("hardware_name", ""),
                        severity=SeverityEnum(item.get("severity", "info").lower()),
                        issue=item.get("issue", ""),
                        recommendation=item.get("recommendation", "")
                    )
                )
                
            return AuditReport(
                issues=issues,
                summary=data.get("summary", "Audit completed.")
            )
        except Exception as e:
            print(f"Error during audit: {e}")
            raise AuditGenerationError(detail=f"Audit failed: {str(e)}")
