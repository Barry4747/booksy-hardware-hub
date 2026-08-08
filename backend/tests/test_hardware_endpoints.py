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

def test_update_hardware_status_in_use_forbidden(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    update_resp = client.put(f"/api/hardware/{hw_id}", json={"status": "In Use"})
    assert update_resp.status_code == 409

def test_update_hardware_status_repair_when_in_use_forbidden(client, test_admin, test_user):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    # user rents it
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    client.post("/api/rentals", json={"hardware_id": hw_id})
    
    # admin tries to set to repair
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    update_resp = client.put(f"/api/hardware/{hw_id}", json={"status": "Repair"})
    assert update_resp.status_code == 409

def test_update_hardware_status_repair_when_available_success(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    update_resp = client.put(f"/api/hardware/{hw_id}", json={"status": "Repair"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Repair"

def test_update_hardware_status_available_when_repair_success(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell", "status": "Repair"})
    hw_id = hw_resp.json()["id"]
    
    update_resp = client.put(f"/api/hardware/{hw_id}", json={"status": "Available"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Available"

def test_delete_in_use_hardware_returns_409(client, test_admin, test_user):
    # Admin creates hardware
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    # User rents it
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    rent_resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    rental_id = rent_resp.json()["id"]
    
    # Admin tries to delete it
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    del_resp = client.delete(f"/api/hardware/{hw_id}")
    
    # Should fail with 409
    assert del_resp.status_code == 409
    assert "active rental" in del_resp.json()["detail"]
    
    # Hardware still exists
    get_hw_resp = client.get(f"/api/hardware/{hw_id}")
    assert get_hw_resp.status_code == 200
    
    # Rental still exists
    get_rent_resp = client.get(f"/api/rentals/{rental_id}")
    assert get_rent_resp.status_code == 200
