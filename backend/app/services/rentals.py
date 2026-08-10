from typing import Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories.rentals import RentalRepository
from app.repositories.hardware import HardwareRepository
from app.schemas.rental import RentalResponse
from app.models.hardware import HardwareStatus
from app.models.rental import RentalStatus
from app.exceptions.rentals import RentalNotFoundError, HardwareUnavailableError, RentalAlreadyReturnedException, RentalNotOwnedException
from app.exceptions.hardware import HardwareNotFoundError

class RentalService:
    def __init__(self, db: Session, rental_repo: RentalRepository, hw_repo: HardwareRepository):
        self.db = db
        self.rental_repo = rental_repo
        self.hw_repo = hw_repo

    def get_rental(self, id: int) -> RentalResponse:
        rental = self.rental_repo.get_by_id(id)
        if not rental:
            raise RentalNotFoundError()
        return RentalResponse.model_validate(rental)

    def list_rentals(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, sort_by: str | None = None, sort_desc: bool = False) -> list[RentalResponse]:
        rentals = self.rental_repo.list(skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc)
        return [RentalResponse.model_validate(r) for r in rentals]

    def create_rental(self, hardware_id: int, user_id: int) -> RentalResponse:
        """
        Creates a new rental and marks the hardware as 'In Use' within a single transaction.
        Raises: HardwareUnavailableError if the hardware is not available.
        """
        hw = self.hw_repo.get_by_id(hardware_id)
        if not hw:
            raise HardwareNotFoundError()
            
        if hw.status != HardwareStatus.AVAILABLE:
            raise HardwareUnavailableError()
            
        self.hw_repo.update(hw, {"status": HardwareStatus.IN_USE})
        rental = self.rental_repo.create(hardware_id=hardware_id, user_id=user_id)
        
        try:
            self.db.commit()
            return RentalResponse.model_validate(rental)
        except Exception as e:
            self.db.rollback()
            raise e

    def return_rental(self, id: int, user_id: int, is_admin: bool = False) -> RentalResponse:
        """
        Marks a rental as returned and restores hardware to 'Available' within a single transaction.
        Raises: RentalNotOwnedException if a regular user tries to return another user's rental.
        """
        rental = self.rental_repo.get_by_id(id)
        if not rental:
            raise RentalNotFoundError()
            
        if not is_admin and rental.user_id != user_id:
            raise RentalNotOwnedException()
            
        if rental.status == RentalStatus.RETURNED or rental.returned_at is not None:
            raise RentalAlreadyReturnedException()
            
        hw = self.hw_repo.get_by_id(rental.hardware_id)
        if not hw:
            raise HardwareNotFoundError()
            
        self.hw_repo.update(hw, {"status": HardwareStatus.AVAILABLE})
        rental = self.rental_repo.update(rental, {
            "status": RentalStatus.RETURNED,
            "returned_at": datetime.now(timezone.utc)
        })
        
        try:
            self.db.commit()
            return RentalResponse.model_validate(rental)
        except Exception as e:
            self.db.rollback()
            raise e
