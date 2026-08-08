import pytest
from app.services.hardware import HardwareService
from app.repositories.hardware import HardwareRepository
from app.exceptions.hardware import HardwareNotFoundError
from app.models.hardware import HardwareStatus
from app.schemas.hardware import HardwareCreate, HardwareUpdate
from app.repositories.rentals import RentalRepository

def test_create_hardware(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    hw_in = HardwareCreate(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw = service.create_hardware(hw_in)
    
    assert hw.id is not None
    assert hw.name == "MacBook"

def test_get_hardware_success(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    hw_in = HardwareCreate(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw = service.create_hardware(hw_in)
    
    fetched = service.get_hardware(hw.id)
    assert fetched.id == hw.id

def test_get_hardware_not_found(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    with pytest.raises(HardwareNotFoundError):
        service.get_hardware(999)

def test_update_hardware(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    hw_in = HardwareCreate(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw = service.create_hardware(hw_in)
    
    update_in = HardwareUpdate(status=HardwareStatus.REPAIR)
    updated = service.update_hardware(hw.id, update_in)
    
    assert updated.status == HardwareStatus.REPAIR

def test_update_hardware_not_found(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    update_in = HardwareUpdate(status=HardwareStatus.REPAIR)
    with pytest.raises(HardwareNotFoundError):
        service.update_hardware(999, update_in)

def test_delete_hardware(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    hw_in = HardwareCreate(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw = service.create_hardware(hw_in)
    
    service.delete_hardware(hw.id)
    
    with pytest.raises(HardwareNotFoundError):
        service.get_hardware(hw.id)

def test_delete_hardware_not_found(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    with pytest.raises(HardwareNotFoundError):
        service.delete_hardware(999)

def test_list_hardware(db_session):
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    service.create_hardware(HardwareCreate(name="MacBook", brand="Apple"))
    service.create_hardware(HardwareCreate(name="ThinkPad", brand="Lenovo"))
    
    items = service.list_hardware(limit=10)
    assert len(items) >= 2

def test_cannot_set_status_to_in_use_directly(db_session):
    from app.exceptions.hardware import InvalidStatusTransitionError
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    
    hw_in = HardwareCreate(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw = service.create_hardware(hw_in)
    
    update_in = HardwareUpdate(status=HardwareStatus.IN_USE)
    with pytest.raises(InvalidStatusTransitionError):
        service.update_hardware(hw.id, update_in)

def test_cannot_set_repair_when_hardware_rented(db_session, test_user):
    from app.exceptions.hardware import InvalidStatusTransitionError
    from app.services.rentals import RentalService
    
    repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = HardwareService(db_session, repo, rental_repo)
    rental_service = RentalService(db_session, rental_repo, repo)
    
    hw_in = HardwareCreate(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw = service.create_hardware(hw_in)
    
    # Rent it
    rental_service.create_rental(hw.id, test_user.id)
    
    update_in = HardwareUpdate(status=HardwareStatus.REPAIR)
    with pytest.raises(InvalidStatusTransitionError):
        service.update_hardware(hw.id, update_in)
