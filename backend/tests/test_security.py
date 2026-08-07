import pytest
from datetime import timedelta
from jose import jwt
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

def test_password_hashing():
    password = "supersecretpassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    user_id = 1
    token = create_access_token(subject=user_id)
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload

def test_create_refresh_token():
    user_id = 1
    token = create_refresh_token(subject=user_id)
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"
    assert "exp" in payload

def test_decode_token_expired():
    token = create_access_token(subject=1, expires_delta=timedelta(seconds=-1))
    with pytest.raises(Exception):
        decode_token(token)
