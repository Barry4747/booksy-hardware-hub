import pytest
from datetime import datetime
from app.models.hardware import HardwareStatus

def test_create_rental(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    
    assert resp.status_code == 201
    assert resp.json()["hardware_id"] == hw_id
    assert resp.json()["user_id"] == test_user.id
    
    # Verify hardware status changed to IN_USE
    hw_get = client.get(f"/api/hardware/{hw_id}")
    assert hw_get.json()["status"] == HardwareStatus.IN_USE.value

def test_create_rental_unavailable(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell", "status": HardwareStatus.IN_USE.value})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    
    assert resp.status_code == 409

def test_return_rental(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    rent_resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    rental_id = rent_resp.json()["id"]
    
    ret_resp = client.patch(f"/api/rentals/{rental_id}", json={"returned_at": datetime.now().isoformat()})
    assert ret_resp.status_code == 200
    assert ret_resp.json()["returned_at"] is not None
    
    hw_get = client.get(f"/api/hardware/{hw_id}")
    assert hw_get.json()["status"] == HardwareStatus.AVAILABLE.value

def test_list_rentals(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    client.post("/api/rentals", json={"hardware_id": hw_id})
    
    list_resp = client.get("/api/rentals")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1
    
    filtered = client.get(f"/api/rentals?hardware_id={hw_id}")
    assert len(filtered.json()) == 1

def test_get_rental(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    rent_resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    rental_id = rent_resp.json()["id"]
    
    get_resp = client.get(f"/api/rentals/{rental_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == rental_id

def test_create_rental_in_repair(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell", "status": HardwareStatus.REPAIR.value})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    assert resp.status_code == 409

def test_create_rental_double_rent(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    resp1 = client.post("/api/rentals", json={"hardware_id": hw_id})
    assert resp1.status_code == 201
    
    resp2 = client.post("/api/rentals", json={"hardware_id": hw_id})
    assert resp2.status_code == 409

def test_return_rental_wrong_user(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    rent_resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    rental_id = rent_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    # create second user
    client.post("/api/users", json={"email": "wrong@example.com", "password": "password123", "is_admin": False})
    
    client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "password123"})
    ret_resp = client.patch(f"/api/rentals/{rental_id}", json={"returned_at": datetime.now().isoformat()})
    assert ret_resp.status_code == 403

def test_return_already_returned(client, test_user, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    hw_resp = client.post("/api/hardware", json={"name": "XPS", "brand": "Dell"})
    hw_id = hw_resp.json()["id"]
    
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    rent_resp = client.post("/api/rentals", json={"hardware_id": hw_id})
    rental_id = rent_resp.json()["id"]
    
    ret_resp1 = client.patch(f"/api/rentals/{rental_id}", json={"returned_at": datetime.now().isoformat()})
    assert ret_resp1.status_code == 200
    
    ret_resp2 = client.patch(f"/api/rentals/{rental_id}", json={"returned_at": datetime.now().isoformat()})
    assert ret_resp2.status_code == 200
