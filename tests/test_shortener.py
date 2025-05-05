from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    user = {"email": "urltester@example.com", "password": "urlpass"}
    client.post("/api/auth/signup", json=user)
    res = client.post("/api/auth/login", json=user)
    return res.json()["access_token"]

def test_url_shortening():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"original_url": "https://example.com"}
    res = client.post("/api/shortener/", json=payload, headers=headers)
    assert res.status_code == 200
    assert "short_code" in res.json()

    short_code = res.json()["short_code"]
    res = client.get(f"/api/shortener/{short_code}")
    assert res.status_code == 200
    assert res.json()["original_url"] == "https://example.com"
