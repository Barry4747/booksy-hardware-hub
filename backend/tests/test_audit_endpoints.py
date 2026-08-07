def test_run_audit_admin(client, test_admin):
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    
    resp = client.post("/api/audit")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "issues" in data

def test_run_audit_user_forbidden(client, test_user):
    client.post("/api/auth/login", json={"email": test_user.email, "password": "password123"})
    
    resp = client.post("/api/audit")
    assert resp.status_code == 403

def test_run_audit_unauthorized(client):
    resp = client.post("/api/audit")
    assert resp.status_code == 401

def test_run_audit_rate_limit(client, test_admin):
    from app.core.config import settings
    from app.core.rate_limit import limiter
    
    # Clear slowapi in-memory storage so previous tests don't affect this test
    limiter._storage.reset()
    
    client.post("/api/auth/login", json={"email": test_admin.email, "password": "admin123"})
    
    # Hit the limit
    for _ in range(settings.AUDIT_RATE_LIMIT):
        resp = client.post("/api/audit")
        assert resp.status_code == 200
        
    # The next one should fail with 429
    resp_blocked = client.post("/api/audit")
    assert resp_blocked.status_code == 429
    assert resp_blocked.json()["error"] == f"Rate limit exceeded: {settings.AUDIT_RATE_LIMIT} per 1 minute"
