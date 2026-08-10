from fastapi import APIRouter, Depends, status, HTTPException
from app.api.dependencies.auth import require_admin, get_current_user
from app.api.dependencies.core import get_user_service
from app.services.users import UserService
from app.schemas.user import UserCreate, UserResponse, DeleteUserResponse
from app.models.user import User

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

@router.delete("/{id}", response_model=DeleteUserResponse, dependencies=[Depends(require_admin)])
def delete_user(
    id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    if id == current_user.id:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete your own account."
        )
    return user_service.delete_user(id)

@router.get("", response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def list_users(
    user_service: UserService = Depends(get_user_service)
):
    return user_service.list_users()
