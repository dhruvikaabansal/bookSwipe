from fastapi.testclient import TestClient
from app.main import app
import os
import pytest

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_demo_login():
    response = client.post("/auth/demo-login")
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user_id"] == "demo_user"

@pytest.mark.skipif(not os.path.exists("artifacts/faiss.index"), reason="Index not built")
def test_recommend():
    # Login first
    login_res = client.post("/auth/demo-login")
    user_id = login_res.json()["user_id"]
    
    # Get recs
    response = client.get(f"/recommend?user_id={user_id}&n=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "book_id" in data[0]
        assert "title" in data[0]
