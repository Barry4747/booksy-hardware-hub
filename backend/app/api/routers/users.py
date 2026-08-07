from fastapi import APIRouter, Depends, status
from app.api.dependencies.auth import require_admin
from app.api.dependencies.core import get_user_service
from app.services.users import UserService
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return user_service.create_user(
        email=user_in.email,
        password=user_in.password,
        is_admin=user_in.is_admin
    )
