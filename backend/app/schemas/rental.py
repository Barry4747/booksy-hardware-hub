from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class RentalBase(BaseModel):
    hardware_id: int
    user_id: int
    returned_at: Optional[datetime] = None

class RentalResponse(RentalBase):
    id: int
    rented_at: datetime

    model_config = ConfigDict(from_attributes=True)
