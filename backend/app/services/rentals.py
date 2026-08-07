from typing import Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.repositories.rentals import RentalRepository
from app.repositories.hardware import HardwareRepository
from app.schemas.rental import RentalResponse, RentalUpdate
from app.models.hardware import HardwareStatus
from app.models.rental import RentalStatus
from app.exceptions.rentals import RentalNotFoundError, HardwareUnavailableError
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
        hw = self.hw_repo.get_by_id(hardware_id)
        if not hw:
            raise HardwareNotFoundError()
            
        if hw.status != HardwareStatus.AVAILABLE:
            raise HardwareUnavailableError()
            
        self.hw_repo.update(hw, {"status": HardwareStatus.IN_USE})
        rental = self.rental_repo.create(hardware_id=hardware_id, user_id=user_id)
        
        self.db.commit()
        return RentalResponse.model_validate(rental)

    def update_rental(self, id: int, updates: RentalUpdate) -> RentalResponse:
        rental = self.rental_repo.get_by_id(id)
        if not rental:
            raise RentalNotFoundError()
            
        update_data = updates.model_dump(exclude_unset=True)
        if not update_data:
            return RentalResponse.model_validate(rental)
            
        # Determine if we need to return the device based on returned_at or status changes
        is_returning = False
        
        if "returned_at" in update_data and update_data["returned_at"] is not None and rental.returned_at is None:
            is_returning = True
            update_data["status"] = RentalStatus.RETURNED
            
        if "status" in update_data and update_data["status"] == RentalStatus.RETURNED and rental.status != RentalStatus.RETURNED:
            is_returning = True
            if "returned_at" not in update_data or update_data["returned_at"] is None:
                update_data["returned_at"] = datetime.now()
                
        if is_returning:
            hw = self.hw_repo.get_by_id(rental.hardware_id)
            if hw:
                self.hw_repo.update(hw, {"status": HardwareStatus.AVAILABLE})
                    
        rental = self.rental_repo.update(rental, update_data)
        self.db.commit()
        
        return RentalResponse.model_validate(rental)
