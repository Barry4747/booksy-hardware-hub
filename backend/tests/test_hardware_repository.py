import pytest
from app.repositories.hardware import HardwareRepository
from app.models.hardware import HardwareStatus

def test_hardware_repository_create(db_session):
    repo = HardwareRepository(db_session)
    hw = repo.create(name="MacBook Pro", brand="Apple", status=HardwareStatus.AVAILABLE)
    assert hw.id is not None
    assert hw.name == "MacBook Pro"

def test_hardware_repository_get_by_id(db_session):
    repo = HardwareRepository(db_session)
    hw = repo.create(name="Dell XPS", brand="Dell", status=HardwareStatus.AVAILABLE)
    
    fetched = repo.get_by_id(hw.id)
    assert fetched is not None
    assert fetched.brand == "Dell"

def test_hardware_repository_update(db_session):
    repo = HardwareRepository(db_session)
    hw = repo.create(name="Thinkpad", brand="Lenovo", status=HardwareStatus.AVAILABLE)
    
    updated = repo.update(hw, {"status": HardwareStatus.IN_USE})
    assert updated.status == HardwareStatus.IN_USE

def test_hardware_repository_delete(db_session):
    repo = HardwareRepository(db_session)
    hw = repo.create(name="Thinkpad", brand="Lenovo", status=HardwareStatus.AVAILABLE)
    
    hw_id = hw.id
    repo.delete(hw)
    
    assert repo.get_by_id(hw_id) is None

def test_hardware_repository_list_and_filters(db_session):
    repo = HardwareRepository(db_session)
    repo.create(name="MacBook Pro", brand="Apple", status=HardwareStatus.AVAILABLE)
    repo.create(name="MacBook Air", brand="Apple", status=HardwareStatus.IN_USE)
    repo.create(name="XPS", brand="Dell", status=HardwareStatus.AVAILABLE)
    
    # Test simple list
    items = repo.list()
    assert len(items) >= 3
    
    # Test pagination
    paginated = repo.list(skip=0, limit=2)
    assert len(paginated) == 2
    
    # Test filtering
    apple_items = repo.list(filters={"brand": "Apple"})
    assert len(apple_items) == 2
    
    available_apple = repo.list(filters={"brand": "Apple", "status": HardwareStatus.AVAILABLE})
    assert len(available_apple) == 1
    
    # Test sorting
    sorted_items = repo.list(sort_by="name", sort_desc=True)
    assert sorted_items[0].name == "XPS" # Because X is at the end of alphabet, descending puts it first
