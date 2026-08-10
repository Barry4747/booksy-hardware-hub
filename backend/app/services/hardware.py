from typing import Any
from sqlalchemy.orm import Session
from app.repositories.hardware import HardwareRepository
from app.schemas.hardware import HardwareCreate, HardwareUpdate, HardwareResponse
from app.exceptions.hardware import HardwareNotFoundError, InvalidStatusTransitionError, HardwareStillRentedError
from app.repositories.rentals import RentalRepository
from app.models.hardware import HardwareStatus

class HardwareService:
    def __init__(self, db: Session, hw_repo: HardwareRepository, rental_repo: RentalRepository):
        self.db = db
        self.hw_repo = hw_repo
        self.rental_repo = rental_repo

    def get_hardware(self, id: int) -> HardwareResponse:
        hw = self.hw_repo.get_by_id(id)
        if not hw:
            raise HardwareNotFoundError()
        return HardwareResponse.model_validate(hw)

    def list_hardware(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, search: str | None = None, sort_by: str | None = None, sort_desc: bool = False) -> list[HardwareResponse]:
        hws = self.hw_repo.list(skip=skip, limit=limit, filters=filters, search=search, sort_by=sort_by, sort_desc=sort_desc)
        return [HardwareResponse.model_validate(hw) for hw in hws]

    def create_hardware(self, hardware_in: HardwareCreate) -> HardwareResponse:
        hw = self.hw_repo.create(**hardware_in.model_dump())
        self.db.commit()
        return HardwareResponse.model_validate(hw)

    def update_hardware(self, id: int, hardware_in: HardwareUpdate) -> HardwareResponse:
        """
        Updates hardware attributes while enforcing status transition rules.
        Raises: InvalidStatusTransitionError if attempting to set 'In Use' directly or 'Repair' while rented.
        """
        hw = self.hw_repo.get_by_id(id)
        if not hw:
            raise HardwareNotFoundError()
            
        if hardware_in.status == HardwareStatus.IN_USE:
            raise InvalidStatusTransitionError(
                detail="Cannot set status to 'In Use' directly. Use the rental endpoint instead."
            )
            
        if hardware_in.status == HardwareStatus.REPAIR:
            active_rental = self.rental_repo.get_active_by_hardware(id)
            if active_rental:
                raise InvalidStatusTransitionError(
                    detail="Cannot mark as Repair: hardware has an active rental. Force-return it first."
                )
        
        update_data = hardware_in.model_dump(exclude_unset=True)
        if update_data:
            hw = self.hw_repo.update(hw, update_data)
            self.db.commit()
            
        return HardwareResponse.model_validate(hw)

    def delete_hardware(self, id: int) -> None:
        """
        Deletes a hardware item if it has no active rentals.
        Raises: HardwareStillRentedError if an active rental exists.
        """
        hw = self.hw_repo.get_by_id(id)
        if not hw:
            raise HardwareNotFoundError()
            
        active_rental = self.rental_repo.get_active_by_hardware(id)
        if active_rental:
            raise HardwareStillRentedError(
                detail="Cannot delete hardware with an active rental. Force-return it first."
            )
        
        self.hw_repo.delete(hw)
        self.db.commit()
