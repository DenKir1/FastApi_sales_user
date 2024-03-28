# import pytest
# from tortoise import Tortoise
# from tortoise.contrib.test import finalizer, initializer
#
# import config
#
# db_ = config.DATABASE_URL_TEST
#
#
# @pytest.fixture(scope="session")
# async def db_url():
#     return db_
#
#
# @pytest.fixture(scope="session")
# async def db(db_url):
#     await initializer(["users.models", "sales.models"], db_url=db_url)
#     yield
#     await finalizer()
#
#
# @pytest.fixture(scope="function")
# async def db_connection(db, db_url):
#     async with Tortoise.get_connection("default"):
#         yield




    # import pytest
# from httpx import AsyncClient
# from tortoise import Tortoise
#
# import config
# from main import app
#
# DB_URL = config.DATABASE_URL_TEST
#
#
# async def init_db(db_url, create_db: bool = False, schemas: bool = False) -> None:
#     """Initial database connection"""
#     await Tortoise.init(
#         db_url=db_url,
#         modules={"models": [
#             "aerich.models",
#             "users.models",
#             "sales.models",
#         ]},
#         _create_db=create_db
#     )
#     if create_db:
#         print(f"Database created! {db_url = }")
#     if schemas:
#         await Tortoise.generate_schemas()
#         print("Success to generate schemas")
#
#
# async def init(db_url: str = DB_URL):
#     await init_db(db_url, True, True)
#
#
# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"
#
#
# @pytest.fixture(scope="session")
# async def client():
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         print("Client is ready")
#         yield client
#
#
# @pytest.fixture(scope="session", autouse=True)
# async def initialize_tests():
#     await init()
#     yield
#     await Tortoise._drop_databases()
