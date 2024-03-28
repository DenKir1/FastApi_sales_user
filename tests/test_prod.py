from main import app
from starlette.testclient import TestClient


def test_homepage():
    with TestClient(app) as client:
        # Application's lifespan is called on entering the block.
        response = client.get("/users/register")
        print(response.json())
        assert response.status_code == 400





# import pytest
# from httpx import AsyncClient
#
# from main import app
#
#
# @pytest.mark.anyio
# async def test_root():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get("/users/register")
#     print(response.json())
#     assert response.status_code == 200

