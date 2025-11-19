from fastapi.testclient import TestClient

from arua.app import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data.get("message") == "ARUA is up"


def test_add_endpoint():
    response = client.get("/add?a=2&b=3")
    assert response.status_code == 200
    data = response.json()
    assert data.get("result") == 5


def test_multiply_endpoint():
    response = client.post("/multiply", json={"a": 4, "b": 5})
    assert response.status_code == 200
    data = response.json()
    assert data.get("result") == 20
