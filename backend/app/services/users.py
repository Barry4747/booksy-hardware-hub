from sqlalchemy.orm import Session
from app.repositories.users import UserRepository
from app.core.security import get_password_hash
from app.exceptions.users import UserAlreadyExistsError, UserNotFoundError, UserError
from app.schemas.user import UserResponse, DeleteUserResponse
from app.models.rental import RentalStatus
from app.models.hardware import HardwareStatus
from datetime import datetime, timezone

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

    def delete_user(self, user_id: int) -> DeleteUserResponse:
        """
        Deletes a user and force-returns any of their active hardware rentals.
        Raises: UserNotFoundError if missing, UserError if attempting to delete the last admin.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
            
        if user.is_admin:
            admin_count = self.user_repo.count_admins()
            if admin_count <= 1:
                raise UserError(
                    detail="Cannot delete the last administrator.",
                    status_code=409
                )
            
        force_closed = 0
        for rental in user.rentals:
            if rental.returned_at is None:
                rental.returned_at = datetime.now(timezone.utc)
                rental.status = RentalStatus.RETURNED
                if rental.hardware:
                    rental.hardware.status = HardwareStatus.AVAILABLE
                force_closed += 1
                
        self.user_repo.delete(user)
        self.db.commit()
        
        if force_closed > 0:
            return DeleteUserResponse(
                message="User deleted. Active rentals were force-closed and hardware returned to available.",
                force_closed_rentals=force_closed
            )
        else:
            return DeleteUserResponse(
                message="User deleted.",
                force_closed_rentals=0
            )

    def list_users(self) -> list[UserResponse]:
        users = self.user_repo.list()
        return [UserResponse.model_validate(u) for u in users]
