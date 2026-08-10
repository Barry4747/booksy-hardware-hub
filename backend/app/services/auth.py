from fastapi import Response
from app.exceptions.auth import InvalidCredentialsError, TokenMissingError, InvalidTokenError, UserNotFoundError
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
            raise InvalidCredentialsError()
        
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="none",  # IMPORTANT for cross-domain requests (Vercel -> Railway)
            secure=True,     # IMPORTANT: required when samesite="none" (works only over HTTPS)
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="none",  # IMPORTANT for cross-domain requests (Vercel -> Railway)
            secure=True,     # IMPORTANT: required when samesite="none" (works only over HTTPS)
            path="/",
        )
        
        # db.commit() would go here if we were updating a last_login field
        return UserResponse.model_validate(user)

    def logout(self, response: Response) -> None:
        response.delete_cookie("access_token", samesite="none", secure=True)
        response.delete_cookie("refresh_token", samesite="none", secure=True)

    def refresh(self, refresh_token: str, response: Response) -> UserResponse:
        if not refresh_token:
            raise TokenMissingError(detail="Refresh token missing")
            
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise InvalidTokenError(detail="Invalid token type")
            user_id = int(payload.get("sub"))
        except Exception:
            raise InvalidTokenError()
            
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
            
        access_token = create_access_token(subject=user.id)
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            samesite="none",  # IMPORTANT for cross-domain requests (Vercel -> Railway)
            secure=True,     # IMPORTANT: required when samesite="none" (works only over HTTPS)
        )
        
        return UserResponse.model_validate(user)

    def me(self, current_user: User) -> UserResponse:
        return UserResponse.model_validate(current_user)
