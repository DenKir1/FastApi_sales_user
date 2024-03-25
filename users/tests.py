
import pytest
from httpx import AsyncClient

from main import app
from models import User
from fastapi.testclient import TestClient

client = TestClient(app)

def test_get_protected_route():
    response = client.get("/protected-route", headers={"Authorization": "Bearer " + get_test_jwt()})
    assert response.status_code == 200

def test_get_protected_route_without_token():
    response = client.get("/protected-route")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_create_user(client: AsyncClient):  # nosec
    response = await client.post("/users", json={"username": "admin"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == "admin"
    assert "id" in data
    user_id = data["id"]

    user_obj = await User.get(id=user_id)
    assert user_obj.id == user_id
