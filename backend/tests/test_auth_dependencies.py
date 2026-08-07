import pytest
from fastapi import Request
from app.api.dependencies.auth import get_current_user, require_admin
from app.exceptions.auth import TokenMissingError, InvalidTokenError, UserNotFoundError, NotEnoughPrivilegesError
from app.repositories.users import UserRepository
from app.core.security import create_access_token, create_refresh_token

class MockRequest(Request):
    def __init__(self, cookies: dict):
        self._cookies = cookies
    
    @property
    def cookies(self):
        return self._cookies

def test_get_current_user_success(db_session, test_user):
    access_token = create_access_token(subject=test_user.id)
    req = MockRequest(cookies={"access_token": f"Bearer {access_token}"})
    repo = UserRepository(db_session)
    
    user = get_current_user(request=req, user_repo=repo)
    assert user.id == test_user.id

def test_get_current_user_missing_token(db_session):
    req = MockRequest(cookies={})
    repo = UserRepository(db_session)
    
    with pytest.raises(TokenMissingError):
        get_current_user(request=req, user_repo=repo)

def test_get_current_user_invalid_prefix(db_session):
    req = MockRequest(cookies={"access_token": "NotBearer token123"})
    repo = UserRepository(db_session)
    
    with pytest.raises(TokenMissingError):
        get_current_user(request=req, user_repo=repo)

def test_get_current_user_invalid_type(db_session, test_user):
    refresh_token = create_refresh_token(subject=test_user.id)
    req = MockRequest(cookies={"access_token": f"Bearer {refresh_token}"})
    repo = UserRepository(db_session)
    
    with pytest.raises(InvalidTokenError):
        get_current_user(request=req, user_repo=repo)

def test_get_current_user_garbage_token(db_session):
    req = MockRequest(cookies={"access_token": "Bearer garbage"})
    repo = UserRepository(db_session)
    
    with pytest.raises(InvalidTokenError):
        get_current_user(request=req, user_repo=repo)

def test_get_current_user_unknown_user(db_session, test_user):
    access_token = create_access_token(subject=test_user.id)
    req = MockRequest(cookies={"access_token": f"Bearer {access_token}"})
    repo = UserRepository(db_session)
    
    db_session.delete(test_user)
    db_session.flush()
    
    with pytest.raises(UserNotFoundError):
        get_current_user(request=req, user_repo=repo)

def test_require_admin_success(test_admin):
    user = require_admin(current_user=test_admin)
    assert user.id == test_admin.id

def test_require_admin_forbidden(test_user):
    with pytest.raises(NotEnoughPrivilegesError):
        require_admin(current_user=test_user)
