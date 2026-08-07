import pytest

def test_create_user_as_admin_success(client, test_admin):
    # Log in as admin
    client.post("/api/auth/login", json={
        "email": test_admin.email,
        "password": "admin123"
    })
    
    response = client.post("/api/users", json={
        "email": "new_user@example.com",
        "password": "newpassword",
        "is_admin": False
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new_user@example.com"
    assert data["is_admin"] is False
    assert "id" in data

def test_create_user_as_regular_user_forbidden(client, test_user):
    # Log in as normal user
    client.post("/api/auth/login", json={
        "email": test_user.email,
        "password": "password123"
    })
    
    response = client.post("/api/users", json={
        "email": "new_user2@example.com",
        "password": "newpassword",
        "is_admin": False
    })
    assert response.status_code == 403

def test_create_user_unauthorized(client):
    response = client.post("/api/users", json={
        "email": "new_user3@example.com",
        "password": "newpassword",
        "is_admin": False
    })
    assert response.status_code == 401
    
def test_create_user_duplicate_email(client, test_admin, test_user):
    # Log in as admin
    client.post("/api/auth/login", json={
        "email": test_admin.email,
        "password": "admin123"
    })
    
    response = client.post("/api/users", json={
        "email": test_user.email,
        "password": "newpassword",
        "is_admin": False
    })
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists"
