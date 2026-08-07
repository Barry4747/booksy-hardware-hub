import pytest
from fastapi import Response
from app.services.auth import AuthService
from app.repositories.users import UserRepository
from app.exceptions.auth import InvalidCredentialsError, TokenMissingError, InvalidTokenError, UserNotFoundError
from app.core.security import create_access_token

class MockResponse(Response):
    def __init__(self):
        super().__init__()
        self.cookies_set = {}
        self.cookies_deleted = set()
        
    def set_cookie(self, key, value, **kwargs):
        self.cookies_set[key] = value

    def delete_cookie(self, key, **kwargs):
        self.cookies_deleted.add(key)

def test_login_success(db_session, test_user):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    user_response = service.login(test_user.email, "password123", resp)
    
    assert user_response.email == test_user.email
    assert "access_token" in resp.cookies_set
    assert "refresh_token" in resp.cookies_set
    assert resp.cookies_set["access_token"].startswith("Bearer ")

def test_login_invalid_password(db_session, test_user):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    with pytest.raises(InvalidCredentialsError):
        service.login(test_user.email, "wrongpassword", resp)

def test_login_unknown_user(db_session):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    with pytest.raises(InvalidCredentialsError):
        service.login("nobody@example.com", "password", resp)

def test_logout(db_session):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    service.logout(resp)
    
    assert "access_token" in resp.cookies_deleted
    assert "refresh_token" in resp.cookies_deleted

def test_refresh_success(db_session, test_user):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    service.login(test_user.email, "password123", resp)
    refresh_token = resp.cookies_set["refresh_token"]
    
    resp2 = MockResponse()
    user_response = service.refresh(refresh_token, resp2)
    
    assert user_response.email == test_user.email
    assert "access_token" in resp2.cookies_set

def test_refresh_missing_token(db_session):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    with pytest.raises(TokenMissingError):
        service.refresh(None, resp)

def test_refresh_invalid_type(db_session, test_user):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    access_token = create_access_token(subject=test_user.id)
    
    with pytest.raises(InvalidTokenError):
        service.refresh(access_token, resp)

def test_refresh_invalid_token(db_session):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    with pytest.raises(InvalidTokenError):
        service.refresh("garbage_token", resp)

def test_refresh_unknown_user(db_session, test_user):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    resp = MockResponse()
    
    service.login(test_user.email, "password123", resp)
    refresh_token = resp.cookies_set["refresh_token"]
    
    db_session.delete(test_user)
    db_session.flush()
    
    with pytest.raises(UserNotFoundError):
        service.refresh(refresh_token, resp)

def test_me(db_session, test_user):
    repo = UserRepository(db_session)
    service = AuthService(db=db_session, user_repo=repo)
    
    user_resp = service.me(test_user)
    assert user_resp.id == test_user.id
