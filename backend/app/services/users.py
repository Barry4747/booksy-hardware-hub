from sqlalchemy.orm import Session
from app.repositories.users import UserRepository
from app.core.security import get_password_hash
from app.exceptions.users import UserAlreadyExistsError
from app.schemas.user import UserResponse

class UserService:
    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo

    def create_user(self, email: str, password: str, is_admin: bool = False) -> UserResponse:
        if self.user_repo.get_by_email(email):
            raise UserAlreadyExistsError()
        
        password_hash = get_password_hash(password)
        user = self.user_repo.create(email=email, password_hash=password_hash, is_admin=is_admin)
        
        self.db.commit()
        return UserResponse.model_validate(user)
