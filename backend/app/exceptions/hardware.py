from fastapi import status

class HardwareError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST, headers: dict | None = None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

class HardwareNotFoundError(HardwareError):
    def __init__(self):
        super().__init__(
            detail="Hardware not found", 
            status_code=status.HTTP_404_NOT_FOUND
        )
