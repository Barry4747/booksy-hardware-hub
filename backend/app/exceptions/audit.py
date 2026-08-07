from fastapi import status

class AuditError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code

class AuditRateLimitExceededError(AuditError):
    def __init__(self):
        super().__init__(
            detail="Too many requests. Please try again later.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
