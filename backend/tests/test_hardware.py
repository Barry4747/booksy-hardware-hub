import pytest
from app.models.hardware import Hardware, HardwareStatus
from app.models.rental import Rental
from app.models.user import User

def test_hardware_cascade_delete_rentals(db_session):
    # Create a user
    user = User(email="cascade@example.com", password_hash="hash")
    db_session.add(user)
    db_session.flush()

    # Create a hardware item
    hardware = Hardware(name="Cascade Laptop", brand="Dell", status=HardwareStatus.AVAILABLE)
    db_session.add(hardware)
    db_session.flush()

    # Create a rental for that item
    rental = Rental(hardware_id=hardware.id, user_id=user.id)
    db_session.add(rental)
    db_session.commit()

    hw_id = hardware.id
    rental_id = rental.id

    # Delete the hardware item
    db_session.delete(hardware)
    db_session.commit()

    # Assert the hardware is gone
    assert db_session.query(Hardware).filter(Hardware.id == hw_id).first() is None

    # Assert the rental is also gone (no orphaned records)
    assert db_session.query(Rental).filter(Rental.id == rental_id).first() is None
