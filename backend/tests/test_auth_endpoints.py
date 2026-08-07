import pytest

def test_api_login_success(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    
    # Check cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

def test_api_login_failure(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect email or password"}

def test_api_me_success(client, test_user):
    client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email

def test_api_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_api_refresh_success(client, test_user):
    client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    
    client.cookies.delete("access_token")
    
    response = client.post("/api/auth/refresh")
    assert response.status_code == 200
    assert "access_token" in response.cookies

def test_api_logout(client, test_user):
    client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    
    assert "access_token" in client.cookies
    
    response = client.post("/api/auth/logout")
    assert response.status_code == 204
    
    assert "access_token" not in client.cookies
    assert "refresh_token" not in client.cookies
