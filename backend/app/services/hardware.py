from typing import Any
from sqlalchemy.orm import Session
from app.repositories.hardware import HardwareRepository
from app.schemas.hardware import HardwareCreate, HardwareUpdate, HardwareResponse
from app.exceptions.hardware import HardwareNotFoundError

class HardwareService:
    def __init__(self, db: Session, hw_repo: HardwareRepository):
        self.db = db
        self.hw_repo = hw_repo

    def get_hardware(self, id: int) -> HardwareResponse:
        hw = self.hw_repo.get_by_id(id)
        if not hw:
            raise HardwareNotFoundError()
        return HardwareResponse.model_validate(hw)

    def list_hardware(self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None, sort_by: str | None = None, sort_desc: bool = False) -> list[HardwareResponse]:
        hws = self.hw_repo.list(skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc)
        return [HardwareResponse.model_validate(hw) for hw in hws]

    def create_hardware(self, hardware_in: HardwareCreate) -> HardwareResponse:
        hw = self.hw_repo.create(**hardware_in.model_dump())
        self.db.commit()
        return HardwareResponse.model_validate(hw)

    def update_hardware(self, id: int, hardware_in: HardwareUpdate) -> HardwareResponse:
        hw = self.hw_repo.get_by_id(id)
        if not hw:
            raise HardwareNotFoundError()
        
        update_data = hardware_in.model_dump(exclude_unset=True)
        if update_data:
            hw = self.hw_repo.update(hw, update_data)
            self.db.commit()
            
        return HardwareResponse.model_validate(hw)

    def delete_hardware(self, id: int) -> None:
        hw = self.hw_repo.get_by_id(id)
        if not hw:
            raise HardwareNotFoundError()
        
        self.hw_repo.delete(hw)
        self.db.commit()
