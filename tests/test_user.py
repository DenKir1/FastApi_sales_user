# import pytest
# from httpx import AsyncClient
#
# from users.models import User
#
# client = AsyncClient()
#
#
# @pytest.mark.asyncio
# async def test_sample(db_connection):
#     name, age = ["sam", 99]
#     assert await User.filter(full_name=name).count() == 0
#     data = {"fullname": "name", "email": "age"}
#     response = await client.post("/users/register", json=data)
#     print(response.json())
#     assert response.status_code == 200
#
#
# # import pytest
# # from httpx import AsyncClient
# # from users.models import User
# #
# #
# # @pytest.mark.anyio
# # async def test_testpost(client: AsyncClient):
# #     name, age = ["sam", 99]
# #     assert await User.filter(full_name=name).count() == 0
# #
# #     data = {"fullname": name, "email": age}
# #     response = await client.post("/testpost", json=data)
# #     assert response.json() == dict(data, id=1)
# #     assert response.status_code == 200
# #
# #     response = await client.get("/users")
# #     assert response.status_code == 200
# #     assert response.json() == [dict(data, id=1)]
# #
# #     assert await User.filter(username=name).count() == 1
