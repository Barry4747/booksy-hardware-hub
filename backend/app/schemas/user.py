from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pydantic import EmailStr

class UserBase(BaseModel):
    email: EmailStr
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DeleteUserResponse(BaseModel):
    message: str
    force_closed_rentals: int
