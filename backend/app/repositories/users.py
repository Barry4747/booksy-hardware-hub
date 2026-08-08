from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> User | None:
        return self.db.query(User).filter(User.id == id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, password_hash: str, is_admin: bool = False) -> User:
        user = User(email=email, password_hash=password_hash, is_admin=is_admin)
        self.db.add(user)
        self.db.flush()
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()

    def list(self) -> list[User]:
        return self.db.query(User).order_by(User.id.desc()).all()
