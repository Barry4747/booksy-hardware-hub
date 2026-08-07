from fastapi import HTTPException, status, Response
from sqlalchemy.orm import Session
from app.repositories.users import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserResponse
from app.models.user import User

class AuthService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo

    def login(self, email: str, password: str, response: Response) -> UserResponse:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="strict",
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            path="/",
        )
        
        # db.commit() would go here if we were updating a last_login field
        return UserResponse.model_validate(user)

    def logout(self, response: Response) -> None:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

    def refresh(self, refresh_token: str, response: Response) -> UserResponse:
        if not refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
            
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            user_id = int(payload.get("sub"))
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
            
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        access_token = create_access_token(subject=user.id)
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="strict",
        )
        
        return UserResponse.model_validate(user)

    def me(self, current_user: User) -> UserResponse:
        return UserResponse.model_validate(current_user)
