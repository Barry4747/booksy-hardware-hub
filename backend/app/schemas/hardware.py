from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
from app.models.hardware import HardwareStatus

class HardwareBase(BaseModel):
    name: str
    brand: str
    purchase_date: Optional[date] = None
    status: HardwareStatus = HardwareStatus.AVAILABLE
    notes: Optional[str] = None
    serial_number: Optional[str] = None

class HardwareCreate(HardwareBase):
    pass

class HardwareUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    purchase_date: Optional[date] = None
    status: Optional[HardwareStatus] = None
    notes: Optional[str] = None
    serial_number: Optional[str] = None

class HardwareResponse(HardwareBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
