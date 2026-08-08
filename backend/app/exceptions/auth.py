from fastapi import status

class AuthError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED, headers: dict | None = None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

class InvalidCredentialsError(AuthError):
    def __init__(self):
        super().__init__(
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

class TokenMissingError(AuthError):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail=detail)

class InvalidTokenError(AuthError):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail=detail)

class UserNotFoundError(AuthError):
    def __init__(self):
        super().__init__(detail="User not found", status_code=status.HTTP_401_UNAUTHORIZED)

class NotEnoughPrivilegesError(AuthError):
    def __init__(self):
        super().__init__(detail="Not enough privileges", status_code=status.HTTP_403_FORBIDDEN)
