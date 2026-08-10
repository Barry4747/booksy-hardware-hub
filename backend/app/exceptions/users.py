from fastapi import status

class UserError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST, headers: dict | None = None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

class UserAlreadyExistsError(UserError):
    def __init__(self):
        super().__init__(
            detail="User with this email already exists", 
            status_code=status.HTTP_409_CONFLICT
        )

class UserNotFoundError(UserError):
    def __init__(self):
        super().__init__(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
