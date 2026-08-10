from typing import Any
from fastapi import APIRouter, Depends, status, Query
from app.api.dependencies.auth import get_current_user, require_admin
from app.api.dependencies.core import get_hardware_service
from app.services.hardware import HardwareService
from app.schemas.hardware import HardwareCreate, HardwareUpdate, HardwareResponse
from app.models.hardware import HardwareStatus

router = APIRouter()

@router.get("", response_model=list[HardwareResponse], dependencies=[Depends(get_current_user)])
def list_hardware(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    brand: str | None = None,
    hw_status: HardwareStatus | None = Query(None, alias="status"),
    search: str | None = None,
    sort_by: str | None = None,
    sort_desc: bool = False,
    hw_service: HardwareService = Depends(get_hardware_service)
):
    filters = {}
    if brand:
        filters["brand"] = brand
    if hw_status:
        filters["status"] = hw_status
        
    return hw_service.list_hardware(
        skip=skip, limit=limit, filters=filters, search=search, sort_by=sort_by, sort_desc=sort_desc
    )

@router.get("/{id}", response_model=HardwareResponse, dependencies=[Depends(get_current_user)])
def get_hardware(id: int, hw_service: HardwareService = Depends(get_hardware_service)):
    return hw_service.get_hardware(id)

@router.post("", response_model=HardwareResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_hardware(
    hw_in: HardwareCreate,
    hw_service: HardwareService = Depends(get_hardware_service)
):
    return hw_service.create_hardware(hw_in)

@router.put("/{id}", response_model=HardwareResponse, dependencies=[Depends(require_admin)])
def update_hardware(
    id: int,
    hw_in: HardwareUpdate,
    hw_service: HardwareService = Depends(get_hardware_service)
):
    return hw_service.update_hardware(id, hw_in)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
def delete_hardware(id: int, hw_service: HardwareService = Depends(get_hardware_service)):
    hw_service.delete_hardware(id)
