from fastapi import APIRouter, Depends, status, Request
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.core import get_audit_service
from app.services.audit import AuditService
from app.schemas.audit import AuditReport
from app.models.user import User
from app.exceptions.auth import NotEnoughPrivilegesError
from app.core.config import settings
from app.core.rate_limit import limiter

router = APIRouter()

@router.post("", response_model=AuditReport, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.AUDIT_RATE_LIMIT}/minute")
def run_audit(
    request: Request,
    current_user: User = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    if not current_user.is_admin:
        raise NotEnoughPrivilegesError()
        
    return audit_service.run_audit()
