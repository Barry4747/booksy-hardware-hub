from fastapi import APIRouter, Depends, status, Query
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.core import get_rental_service
from app.services.rentals import RentalService
from app.schemas.rental import RentalCreate, RentalResponse, RentalUpdate
from app.models.user import User
from app.exceptions.auth import NotEnoughPrivilegesError

router = APIRouter()

@router.get("", response_model=list[RentalResponse])
def list_rentals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    hardware_id: int | None = None,
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    rental_service: RentalService = Depends(get_rental_service)
):
    filters = {}
    if hardware_id:
        filters["hardware_id"] = hardware_id
        
    if not current_user.is_admin:
        filters["user_id"] = current_user.id
    elif user_id:
        filters["user_id"] = user_id
        
    return rental_service.list_rentals(skip=skip, limit=limit, filters=filters)

@router.get("/{id}", response_model=RentalResponse)
def get_rental(
    id: int, 
    current_user: User = Depends(get_current_user),
    rental_service: RentalService = Depends(get_rental_service)
):
    rental = rental_service.get_rental(id)
    if not current_user.is_admin and rental.user_id != current_user.id:
        raise NotEnoughPrivilegesError()
    return rental

@router.post("", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
def create_rental(
    rental_in: RentalCreate,
    current_user: User = Depends(get_current_user),
    rental_service: RentalService = Depends(get_rental_service)
):
    return rental_service.create_rental(
        hardware_id=rental_in.hardware_id, 
        user_id=current_user.id
    )

@router.patch("/{id}", response_model=RentalResponse, dependencies=[Depends(get_current_user)])
def update_rental(
    id: int,
    rental_in: RentalUpdate,
    rental_service: RentalService = Depends(get_rental_service)
):
    return rental_service.update_rental(id, rental_in)
