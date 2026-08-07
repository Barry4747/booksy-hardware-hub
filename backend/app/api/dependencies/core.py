from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.repositories.users import UserRepository
from app.services.auth import AuthService

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(db=db, user_repo=user_repo)
