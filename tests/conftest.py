# import asyncio
# import pytest
# from asgi_lifespan import LifespanManager
# from httpx import AsyncClient
# from src.main import app
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     return asyncio.get_event_loop()
#
#
# @pytest.fixture(scope="module")
# def anyio_backend():
#     return "asyncio"
#
#
# @pytest.fixture(scope="module")
# async def client():
#     async with LifespanManager(app):
#         async with AsyncClient(app=app, base_url="http://test") as c:
#             yield c
