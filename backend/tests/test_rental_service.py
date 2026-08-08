import pytest
from app.services.rentals import RentalService
from app.repositories.rentals import RentalRepository
from app.repositories.hardware import HardwareRepository
from app.models.hardware import HardwareStatus
from app.exceptions.rentals import RentalNotFoundError, HardwareUnavailableError, RentalAlreadyReturnedException, RentalNotOwnedException
from app.exceptions.hardware import HardwareNotFoundError
from app.models.rental import RentalStatus
from datetime import datetime

def test_create_rental_success(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    rental = service.create_rental(hardware_id=hw.id, user_id=test_user.id)
    assert rental.id is not None
    assert rental.hardware_id == hw.id
    
    updated_hw = hw_repo.get_by_id(hw.id)
    assert updated_hw.status == HardwareStatus.IN_USE

def test_create_rental_hardware_not_found(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    with pytest.raises(HardwareNotFoundError):
        service.create_rental(999, test_user.id)

def test_create_rental_hardware_unavailable(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.IN_USE)
    db_session.commit()
    
    with pytest.raises(HardwareUnavailableError):
        service.create_rental(hw.id, test_user.id)

def test_return_rental_success(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    rental = service.create_rental(hardware_id=hw.id, user_id=test_user.id)
    returned = service.return_rental(rental.id, test_user.id)
    
    assert returned.returned_at is not None
    assert returned.status == RentalStatus.RETURNED
    
    updated_hw = hw_repo.get_by_id(hw.id)
    assert updated_hw.status == HardwareStatus.AVAILABLE

def test_return_rental_already_returned(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    rental = service.create_rental(hardware_id=hw.id, user_id=test_user.id)
    service.return_rental(rental.id, test_user.id)
    
    # second time should raise
    with pytest.raises(RentalAlreadyReturnedException):
        service.return_rental(rental.id, test_user.id)

def test_return_rental_not_owned(db_session, test_user, test_admin):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    rental = service.create_rental(hardware_id=hw.id, user_id=test_user.id)
    
    # Try to return by a different non-admin user
    with pytest.raises(RentalNotOwnedException):
        service.return_rental(rental.id, 9999) # some other user_id

def test_return_rental_not_found(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    with pytest.raises(RentalNotFoundError):
        service.return_rental(999, test_user.id)

def test_get_rental(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    created = service.create_rental(hw.id, test_user.id)
    fetched = service.get_rental(created.id)
    
    assert fetched.id == created.id

def test_list_rentals(db_session, test_user):
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    service.create_rental(hw.id, test_user.id)
    items = service.list_rentals(limit=10)
    
    assert len(items) >= 1

def test_atomic_transaction_rollback(db_session, test_user):
    import unittest.mock
    from app.services.rentals import RentalService
    from app.repositories.rentals import RentalRepository
    from app.repositories.hardware import HardwareRepository
    
    hw_repo = HardwareRepository(db_session)
    rental_repo = RentalRepository(db_session)
    service = RentalService(db_session, rental_repo, hw_repo)
    
    hw = hw_repo.create(name="MacBook", brand="Apple", status=HardwareStatus.AVAILABLE)
    db_session.commit()
    
    with unittest.mock.patch.object(db_session, 'commit', side_effect=Exception("DB Error")) as mock_commit:
        with unittest.mock.patch.object(db_session, 'rollback') as mock_rollback:
            with pytest.raises(Exception, match="DB Error"):
                service.create_rental(hw.id, test_user.id)
            
            mock_rollback.assert_called_once()
            
    # Since we mocked rollback, the session state is technically dirty, but we proved it tried to rollback.
    db_session.rollback() # Clean up manually
    
    rentals = rental_repo.list()
    assert not any(r.hardware_id == hw.id for r in rentals)
