from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.repositories.users import UserRepository
from app.repositories.hardware import HardwareRepository
from app.repositories.rentals import RentalRepository
from app.services.auth import AuthService
from app.services.users import UserService
from app.services.hardware import HardwareService
from app.services.rentals import RentalService
from app.services.audit import AuditService

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_hardware_repository(db: Session = Depends(get_db)) -> HardwareRepository:
    return HardwareRepository(db)

def get_rental_repository(db: Session = Depends(get_db)) -> RentalRepository:
    return RentalRepository(db)

def get_auth_service(
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(db=db, user_repo=user_repo)

def get_user_service(
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(db=db, user_repo=user_repo)

def get_hardware_service(
    db: Session = Depends(get_db),
    hw_repo: HardwareRepository = Depends(get_hardware_repository),
    rental_repo: RentalRepository = Depends(get_rental_repository)
) -> HardwareService:
    return HardwareService(db=db, hw_repo=hw_repo, rental_repo=rental_repo)

def get_rental_service(
    db: Session = Depends(get_db),
    rental_repo: RentalRepository = Depends(get_rental_repository),
    hw_repo: HardwareRepository = Depends(get_hardware_repository)
) -> RentalService:
    return RentalService(db=db, rental_repo=rental_repo, hw_repo=hw_repo)

def get_audit_service(
    db: Session = Depends(get_db),
    hw_repo: HardwareRepository = Depends(get_hardware_repository)
) -> AuditService:
    return AuditService(db=db, hw_repo=hw_repo)
