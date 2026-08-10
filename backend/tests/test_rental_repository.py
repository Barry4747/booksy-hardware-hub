import pytest
from datetime import datetime
from app.repositories.rentals import RentalRepository
from app.models.rental import Rental
from app.models.hardware import Hardware, HardwareStatus
from app.models.user import User

def test_rental_repository_create(db_session, test_user):
    # First create hardware manually
    hw = Hardware(name="Test HW", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.add(hw)
    db_session.commit()
    
    repo = RentalRepository(db_session)
    rental = repo.create(hardware_id=hw.id, user_id=test_user.id)
    assert rental.id is not None
    assert rental.hardware_id == hw.id
    assert rental.user_id == test_user.id
    assert rental.returned_at is None

def test_rental_repository_get_by_id(db_session, test_user):
    hw = Hardware(name="Test HW 2", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.add(hw)
    db_session.commit()
    
    repo = RentalRepository(db_session)
    rental = repo.create(hardware_id=hw.id, user_id=test_user.id)
    
    fetched = repo.get_by_id(rental.id)
    assert fetched is not None
    assert fetched.hardware_id == hw.id

def test_rental_repository_update(db_session, test_user):
    hw = Hardware(name="Test HW 3", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.add(hw)
    db_session.commit()
    
    repo = RentalRepository(db_session)
    rental = repo.create(hardware_id=hw.id, user_id=test_user.id)
    
    now = datetime.now()
    updated = repo.update(rental, {"returned_at": now})
    assert updated.returned_at == now

def test_rental_repository_delete(db_session, test_user):
    hw = Hardware(name="Test HW 4", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.add(hw)
    db_session.commit()
    
    repo = RentalRepository(db_session)
    rental = repo.create(hardware_id=hw.id, user_id=test_user.id)
    
    r_id = rental.id
    repo.delete(rental)
    
    assert repo.get_by_id(r_id) is None

def test_rental_repository_list_and_filters(db_session, test_user, test_admin):
    hw1 = Hardware(name="HW A", brand="Apple", status=HardwareStatus.AVAILABLE)
    hw2 = Hardware(name="HW B", brand="Dell", status=HardwareStatus.AVAILABLE)
    db_session.add_all([hw1, hw2])
    db_session.commit()
    
    repo = RentalRepository(db_session)
    repo.create(hardware_id=hw1.id, user_id=test_user.id)
    repo.create(hardware_id=hw2.id, user_id=test_admin.id)
    repo.create(hardware_id=hw1.id, user_id=test_admin.id)
    
    items = repo.list()
    assert len(items) >= 3
    
    admin_rentals = repo.list(filters={"user_id": test_admin.id})
    assert len(admin_rentals) == 2
    
    hw1_rentals = repo.list(filters={"hardware_id": hw1.id})
    assert len(hw1_rentals) == 2

def test_rental_repository_foreign_key_enforcement(db_session, test_user):
    from sqlalchemy.exc import IntegrityError
    
    repo = RentalRepository(db_session)
    # Try to insert a rental with a non-existent hardware_id (e.g., 9999)
    with pytest.raises(IntegrityError):
        repo.create(hardware_id=9999, user_id=test_user.id)
        # Flush is called inside create, so it will trigger the DB exception immediately
