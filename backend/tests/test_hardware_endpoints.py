import pytest
from app.models.hardware import HardwareStatus

def test_create_hardware_admin(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    
    response = client.post("/api/hardware", json={
        "name": "MacBook Air",
        "brand": "Apple"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "MacBook Air"

def test_create_hardware_user_forbidden(client, test_user):
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    
    response = client.post("/api/hardware", json={
        "name": "MacBook Air",
        "brand": "Apple"
    })
    assert response.status_code == 403

def test_list_hardware_authenticated(client, test_user, test_admin):
    # Admin creates hardware
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    client.post("/api/hardware", json={"name": "XPS", "brand": "Dell", "status": HardwareStatus.AVAILABLE.value})
    
    # User lists hardware
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    response = client.get("/api/hardware")
    
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == "XPS"

def test_list_hardware_unauthenticated(client):
    response = client.get("/api/hardware")
    assert response.status_code == 401

def test_get_hardware_authenticated(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    response = client.get(f"/api/hardware/{hw_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == hw_id

def test_update_hardware_admin(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    update_resp = client.put(f"/api/hardware/{hw_id}", json={"name": "XPS 15"})
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "XPS 15"

def test_delete_hardware_admin(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    del_resp = client.delete(f"/api/hardware/{hw_id}")
    assert del_resp.status_code == 204
    
    get_resp = client.get(f"/api/hardware/{hw_id}")
    assert get_resp.status_code == 404
