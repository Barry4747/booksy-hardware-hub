from fastapi import status

class RentalError(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST, headers: dict | None = None):
        self.detail = detail
        self.status_code = status_code
        self.headers = headers

class RentalNotFoundError(RentalError):
    def __init__(self):
        super().__init__(
            detail="Rental not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

class HardwareUnavailableError(RentalError):
    def __init__(self):
        super().__init__(
            detail="Hardware is not available for rental",
            status_code=status.HTTP_409_CONFLICT
        )

class RentalAlreadyReturnedException(RentalError):
    def __init__(self):
        super().__init__(
            detail="Rental has already been returned",
            status_code=status.HTTP_409_CONFLICT
        )

class RentalNotOwnedException(RentalError):
    def __init__(self):
        super().__init__(
            detail="Rental does not belong to the current user",
            status_code=status.HTTP_403_FORBIDDEN
        )
