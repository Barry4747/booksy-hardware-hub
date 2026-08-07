from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.rental import RentalStatus

class RentalBase(BaseModel):
    hardware_id: int
    user_id: int
    returned_at: Optional[datetime] = None
    status: RentalStatus = RentalStatus.ACTIVE

class RentalCreate(BaseModel):
    hardware_id: int

class RentalUpdate(BaseModel):
    returned_at: Optional[datetime] = None
    status: Optional[RentalStatus] = None

class RentalResponse(RentalBase):
    id: int
    rented_at: datetime

    model_config = ConfigDict(from_attributes=True)
