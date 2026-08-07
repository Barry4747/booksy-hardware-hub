from fastapi import APIRouter, Depends, Response, Request, status
from app.services.auth import AuthService
from app.api.dependencies.core import get_auth_service
from app.api.dependencies.auth import get_current_user
from app.schemas.user import UserResponse, UserLogin
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=UserResponse)
def login(login_data: UserLogin, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(login_data.email, login_data.password, response)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, auth_service: AuthService = Depends(get_auth_service)):
    auth_service.logout(response)
    return None

@router.post("/refresh", response_model=UserResponse)
def refresh(request: Request, response: Response, auth_service: AuthService = Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")
    return auth_service.refresh(refresh_token, response)

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user), auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.me(current_user)
