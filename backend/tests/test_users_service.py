import pytest
from app.services.users import UserService
from app.repositories.users import UserRepository
from app.exceptions.users import UserAlreadyExistsError
from app.core.security import verify_password

def test_create_user_success(db_session):
    repo = UserRepository(db_session)
    service = UserService(db=db_session, user_repo=repo)
    
    new_email = "admin2@example.com"
    password = "securepassword"
    
    user_resp = service.create_user(email=new_email, password=password, is_admin=True)
    
    assert user_resp.email == new_email
    assert user_resp.is_admin is True
    assert user_resp.id is not None
    
    # Verify in DB directly
    db_user = repo.get_by_email(new_email)
    assert db_user is not None
    assert verify_password(password, db_user.password_hash)

def test_create_user_already_exists(db_session, test_user):
    repo = UserRepository(db_session)
    service = UserService(db=db_session, user_repo=repo)
    
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        service.create_user(email=test_user.email, password="somepassword", is_admin=False)
        
    assert exc_info.value.status_code == 409

def test_delete_only_admin(db_session, test_admin):
    from app.exceptions.users import UserError
    repo = UserRepository(db_session)
    service = UserService(db=db_session, user_repo=repo)
    
    # test_admin is currently the only admin in the database via the fixtures.
    with pytest.raises(UserError) as exc_info:
        service.delete_user(test_admin.id)
        
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Cannot delete the last administrator."
